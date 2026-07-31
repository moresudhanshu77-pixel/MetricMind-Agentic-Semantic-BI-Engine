import os
import json
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

CUBE_API_URL = os.getenv("CUBE_API_URL")
CUBE_API_TOKEN = os.getenv("CUBE_API_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize the LLM (Llama 3 via Groq)
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0
)

# This describes YOUR governed schema to the LLM — it will only ever
# pick from these exact fields, never invent new ones or write raw SQL.
CUBE_SCHEMA_DESCRIPTION = """
You have access to the following governed metrics via Cube.dev. 
You must ONLY use these exact field names — never invent new ones.

CUBE: fct_orders (order-level data)
Dimensions:
- fct_orders.order_status (values: delivered, shipped, canceled, invoiced, unavailable)
- fct_orders.order_purchase_timestamp (time)
Measures:
- fct_orders.total_revenue (Total Revenue)
- fct_orders.total_estimated_margin (Total Margin)
- fct_orders.margin_pct (Margin % = weighted average, correct governed calculation)
- fct_orders.total_shipping_cost
- fct_orders.count (number of orders)

CUBE: fct_order_items (item-level data, use this for category breakdowns)
Dimensions:
- fct_order_items.product_category (e.g. watches_gifts, bed_bath_table, sports_leisure, etc.)
- fct_order_items.order_status
Measures:
- fct_order_items.total_revenue
- fct_order_items.total_margin
- fct_order_items.margin_pct

CUBE: dim_customers (customer geography)
Dimensions:
- dim_customers.customer_state
- dim_customers.customer_city
"""

def ask_llm_for_query(user_question):
    """Ask the LLM to convert a natural language question into a Cube.dev query (JSON)."""
    system_prompt = f"""You are a data analyst assistant. Convert the user's question into a 
valid Cube.dev query in JSON format, using ONLY the measures and dimensions listed below.

{CUBE_SCHEMA_DESCRIPTION}

Respond with ONLY a valid JSON object in this exact format, nothing else:
{{
  "measures": ["cube.measure_name"],
  "dimensions": ["cube.dimension_name"]
}}

Do not include any explanation, markdown formatting, or extra text — just the raw JSON.
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_question)
    ])

    # Clean up in case the model wraps it in markdown code fences
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").replace("json", "", 1).strip()

    return json.loads(raw)


# Cost governance: hard limits to prevent expensive, unbounded queries
MAX_ROW_LIMIT = 1000
REQUEST_TIMEOUT_SECONDS = 10

def query_cube(query):
    """Send a query to Cube.dev's REST API and return the result, with cost guardrails."""
    
    # Enforce a hard row limit on every query, regardless of what the LLM generated
    query["limit"] = min(query.get("limit", MAX_ROW_LIMIT), MAX_ROW_LIMIT)

    headers = {
        "Authorization": f"Bearer {CUBE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{CUBE_API_URL}/load",
            params={"query": json.dumps(query)},
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        return {"error": "Query took too long and was stopped to control costs. Try a narrower question.", "data": []}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Query failed: {str(e)}", "data": []}

def explain_result(user_question, cube_query, result_data):
    """Ask the LLM to explain the query result in plain, executive-friendly English."""
    explanation_prompt = f"""You are a financial analyst presenting data to an executive.

The user asked: "{user_question}"

You ran this governed query: {json.dumps(cube_query)}

The data returned was: {json.dumps(result_data)}

Write a clear, concise explanation (3-5 sentences) of what this data shows. 
Use plain English, mention specific numbers, and highlight any notable patterns 
(e.g., which category/status has the highest or lowest values). 
Do not make up any numbers not present in the data. 
Do not mention SQL, JSON, or technical implementation details — 
speak like you're briefing a business executive.
"""

    response = llm.invoke([HumanMessage(content=explanation_prompt)])
    return response.content

def classify_question(user_question):
    """Ask the LLM whether this question requires deeper root-cause investigation."""
    classify_prompt = f"""Classify this business question into ONE category:

"simple" - asking for a direct number or breakdown (e.g. "what is revenue by status")
"investigative" - asking WHY something happened, or about a change/drop/increase 
(e.g. "why did margin drop", "why are margins low", "what caused the decline")

Question: "{user_question}"

Respond with ONLY the word "simple" or "investigative", nothing else.
"""
    response = llm.invoke([HumanMessage(content=classify_prompt)])
    return response.content.strip().lower()


def investigate_root_cause(user_question):
    """
    For investigative questions: run the main order-level query first,
    then automatically run a category-level breakdown to find the root cause.
    """
    # Step 1: get the overall picture (order-level margin)
    overview_query = {
        "measures": ["fct_orders.total_revenue", "fct_orders.total_estimated_margin", "fct_orders.margin_pct"],
        "dimensions": ["fct_orders.order_status"]
    }
    overview_result = query_cube(overview_query)
    overview_data = overview_result.get("data", [])

    # Step 2: automatically drill into category-level breakdown to find root cause
    breakdown_query = {
        "measures": ["fct_order_items.total_revenue", "fct_order_items.total_margin", "fct_order_items.margin_pct"],
        "dimensions": ["fct_order_items.product_category"]
    }
    breakdown_result = query_cube(breakdown_query)
    breakdown_data = breakdown_result.get("data", [])

    # Step 3: ask the LLM to synthesize both results into a root-cause explanation
    synthesis_prompt = f"""You are a financial analyst investigating a business question for an executive.

Question: "{user_question}"

Overall order-level data:
{json.dumps(overview_data)}

Category-level breakdown (used to find the root cause):
{json.dumps(breakdown_data)}

Write a clear root-cause analysis (4-6 sentences). Identify which category or 
categories have the lowest margin percentage, since those are likely dragging 
down the overall numbers. Compare them to the highest-performing categories 
for contrast. Use only the real numbers provided — never invent data. 
Speak like you're briefing an executive, no technical jargon.
"""
    response = llm.invoke([HumanMessage(content=synthesis_prompt)])

    return {
        "overview_query": overview_query,
        "overview_data": overview_data,
        "breakdown_query": breakdown_query,
        "breakdown_data": breakdown_data,
        "explanation": response.content
    }

if __name__ == "__main__":
    question = "What is our total revenue and margin percentage by order status?"

    print(f"Question: {question}\n")

    cube_query = ask_llm_for_query(question)
    print("Generated Cube query:")
    print(json.dumps(cube_query, indent=2))
    print()

    result = query_cube(cube_query)
    result_data = result.get("data", [])
    print("Raw data from Cube.dev:")
    print(json.dumps(result_data, indent=2))
    print()

    explanation = explain_result(question, cube_query, result_data)
    print("=" * 60)
    print("MetricMind's Answer:")
    print("=" * 60)
    print(explanation)