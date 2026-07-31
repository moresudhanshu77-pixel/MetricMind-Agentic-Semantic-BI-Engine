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


def query_cube(query):
    """Send a query to Cube.dev's REST API and return the result."""
    headers = {
        "Authorization": f"Bearer {CUBE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(
        f"{CUBE_API_URL}/load",
        params={"query": json.dumps(query)},
        headers=headers
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    question = "What is our total revenue and margin percentage by order status?"

    print(f"Question: {question}\n")

    cube_query = ask_llm_for_query(question)
    print("Generated Cube query:")
    print(json.dumps(cube_query, indent=2))
    print()

    result = query_cube(cube_query)
    print("Result from Cube.dev:")
    print(json.dumps(result.get("data", []), indent=2))