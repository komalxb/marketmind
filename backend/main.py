from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.graph import research_graph
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    report: str
    sources: list[str]
    sub_questions: list[str]
    iterations: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Invoke the graph with initial state
        result = await research_graph.ainvoke({
            "query": request.query,
            "sub_questions": [],
            "search_results": [],
            "evaluation": "",
            "gaps": [],
            "iterations": 0,
            "final_report": "",
            "sources": []
        })
        
        return ResearchResponse(
            report=result["final_report"],
            sources=result["sources"],
            sub_questions=result["sub_questions"],
            iterations=result["iterations"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))