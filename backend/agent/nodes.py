from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .state import ResearchState
from .tools import search_web
from dotenv import load_dotenv
import json

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def plan_node(state: ResearchState) -> dict:
    """
    Takes the user query and breaks it into 3-5 sub-questions
    that will give comprehensive research coverage.
    """
    messages = [
        SystemMessage(content="""You are a financial research planner. 
        Given a market research query, break it down into 3-5 specific sub-questions 
        that together will give comprehensive coverage of the topic.
        
        Return ONLY a JSON array of strings. No preamble, no explanation.
        Example: ["What are current natural gas prices?", "What supply factors are affecting natural gas?"]
        """),
        HumanMessage(content=f"Query: {state['query']}")
    ]
    
    response = llm.invoke(messages)
    
    try:
        sub_questions = json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback if LLM doesn't return clean JSON
        sub_questions = [state['query']]
    
    return {"sub_questions": sub_questions}


def search_node(state: ResearchState) -> dict:
    """
    Searches the web for each sub-question using Tavily.
    Accumulates results across iterations.
    """
    all_results = state.get("search_results", [])
    all_sources = state.get("sources", [])
    
    # On second iteration, search for gaps instead of sub-questions
    questions_to_search = (
        state.get("gaps", []) 
        if state.get("iterations", 0) > 0 
        else state["sub_questions"]
    )
    
    for question in questions_to_search:
        result = search_web(question)
        all_results.extend(result["results"])
        all_sources.extend(result["sources"])
    
    return {
        "search_results": all_results,
        "sources": list(set(all_sources)),  # deduplicate
        "iterations": state.get("iterations", 0) + 1
    }


def evaluate_node(state: ResearchState) -> dict:
    """
    Evaluates whether search results give sufficient coverage
    of the original query. Identifies gaps if not.
    """
    results_summary = "\n\n".join([
        f"Title: {r['title']}\nContent: {r['content'][:300]}..."
        for r in state["search_results"][:10]  # limit context
    ])
    
    messages = [
        SystemMessage(content="""You are a financial research quality evaluator.
        Given a research query and search results, determine if the coverage is sufficient
        to write a comprehensive market research report.
        
        Return ONLY a JSON object with this structure:
        {
            "evaluation": "sufficient" or "needs_more",
            "gaps": ["gap1", "gap2"]  // empty list if sufficient
        }
        
        Be strict — only return "sufficient" if the results genuinely cover
        the key drivers, market sentiment, and risks.
        """),
        HumanMessage(content=f"""
        Original query: {state['query']}
        
        Search results so far:
        {results_summary}
        """)
    ]
    
    response = llm.invoke(messages)
    
    try:
        parsed = json.loads(response.content)
        evaluation = parsed.get("evaluation", "sufficient")
        gaps = parsed.get("gaps", [])
    except json.JSONDecodeError:
        evaluation = "sufficient"
        gaps = []
    
    return {"evaluation": evaluation, "gaps": gaps}


def synthesize_node(state: ResearchState) -> dict:
    """
    Takes all search results and synthesizes a structured
    market research report.
    """
    results_content = "\n\n".join([
        f"Source: {r['title']}\n{r['content']}"
        for r in state["search_results"][:15]  # limit context
    ])
    
    messages = [
        SystemMessage(content="""You are a senior market research analyst.
        Write a structured market research report based on the provided sources.
        
        Format the report exactly like this:
        
        ## Summary
        2-3 sentence overview of the key finding.
        
        ## Key Drivers
        Bullet points of the main factors driving the market.
        
        ## Market Sentiment
        Current sentiment, positioning, and outlook.
        
        ## Risks & Uncertainties
        Key risks and unknowns to watch.
        
        ## Analyst Take
        A brief forward-looking perspective.
        
        Be specific, use numbers where available, and cite sources by title.
        """),
        HumanMessage(content=f"""
        Research query: {state['query']}
        
        Sources:
        {results_content}
        """)
    ]
    
    response = llm.invoke(messages)
    
    return {"final_report": response.content}