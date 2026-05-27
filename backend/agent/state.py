from typing import TypedDict, Annotated
import operator

class ResearchState(TypedDict):
    # The original user query
    query: str
    
    # Sub-questions the planner generates
    sub_questions: list[str]
    
    # Raw search results from Tavily
    search_results: list[dict]
    
    # Whether the evaluator thinks coverage is sufficient
    evaluation: str  # "sufficient" or "needs_more"
    
    # Gaps identified by evaluator if needs_more
    gaps: list[str]
    
    # How many search iterations we've done
    iterations: int
    
    # Final synthesized report
    final_report: str
    
    # Sources to display in frontend
    sources: list[str]