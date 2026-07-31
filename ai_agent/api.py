from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import ask_llm_for_query, query_cube, explain_result, classify_question, investigate_root_cause

app = FastAPI(title="MetricMind Agent API")

# Allow the Next.js frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development; restrict this later for production
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(request: QuestionRequest):
    question = request.question

    classification = classify_question(question)

    if classification == "investigative":
        result = investigate_root_cause(question)
        return {
            "question": question,
            "mode": "investigative",
            "cube_query": result["overview_query"],
            "breakdown_query": result["breakdown_query"],
            "data": result["overview_data"],
            "breakdown_data": result["breakdown_data"],
            "explanation": result["explanation"]
        }
    else:
        cube_query = ask_llm_for_query(question)
        result = query_cube(cube_query)
        result_data = result.get("data", [])
        explanation = explain_result(question, cube_query, result_data)
        return {
            "question": question,
            "mode": "simple",
            "cube_query": cube_query,
            "data": result_data,
            "explanation": explanation
        }

@app.get("/")
def health_check():
    return {"status": "MetricMind Agent API is running"}