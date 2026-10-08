import os
from typing import TypedDict , Annotated
import operator
import re

import psycopg
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    api_key =os.getenv("GROQ_API_KEY"),
    max_tokens=650,
)

DATABASE_URL = os.getenv("DATABASE_URL")


class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage],operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int

def flight_agent(state: TravelState):
    query = state["user_query"]
    # Ask the LLM for origin/destination IATA codes so the flight search matches the request
    codes = llm.invoke([
        SystemMessage(content="Reply with only the origin and destination airport IATA codes as XXX,YYY. If unknown, reply NONE."),
        HumanMessage(content=query),
    ]).content
    match = re.findall(r"\b[A-Z]{3}\b", re.sub(r"<think>.*?</think>", "", codes, flags=re.DOTALL))
    dep, arr = (match + [None, None])[:2]
    flight_data = search_flights(query, dep, arr)
    return{
        "flight_results": flight_data,
        "messages": [
            AIMessage(content=f"Flight results fetched")
        ],
        "llm_calls": state.get("llm_calls",0) + 1
    }


def hotel_agent(state: TravelState):
    # Ask the LLM for just the destination city so the hotel search isn't polluted
    # by words like "flights", "trip" or the origin city
    city = llm.invoke([
        SystemMessage(content="Reply with only the destination city name for this travel request, nothing else."),
        HumanMessage(content=state["user_query"]),
    ]).content
    city = re.sub(r"<think>.*?</think>", "", city, flags=re.DOTALL).strip()
    city = city.splitlines()[0].strip(" .\"'")[:60] if city else ""
    if not city:
        city = state["user_query"]

    query = f"best hotels to stay in {city} with price per night"
    hotel_results = tavily_search(query)

    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content=f"Hotel information fetched for {city}")
        ],
        "llm_calls": state.get("llm_calls",0) + 1
    }

def itinerary_agent(state: TravelState):

    prompt = f"""
    Create a concise day-by-day travel itinerary for the trip length in the user's request
    (if no length is given, plan 3 days). Bullet points only, max 200 words.
    User Query:
    {state['user_query']}

    Flight Results:
    {state['flight_results']}

    Hotel Results:
    {state['hotel_results']}
    """

    response = llm.invoke([
        SystemMessage(
            content="You are a concise travel planner. Keep answers short and under 250 words."
            ),
            HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls",0) + 1
    }

def final_agent(state: TravelState):
    final_prompt = f"""
    Synthesize this travel plan concisely (under 250 words total).
    
    Flights:
    {state['flight_results']}
    
    Hotels:
    {state['hotel_results']}
    
    Itinerary:
    {state['itinerary']}
    """

    response = llm.invoke([
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls",0) + 1
    }


graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)

# Use PostgreSQL for persistent memory when DATABASE_URL is set;
# otherwise fall back to in-memory checkpoints (e.g. on Streamlit Cloud).
if DATABASE_URL:
    _conn = psycopg.connect(DATABASE_URL, autocommit=True)
    checkpointer = PostgresSaver(_conn)
    checkpointer.setup()
else:
    checkpointer = MemorySaver()


app = graph.compile(checkpointer=checkpointer)

if __name__=="__main__":
    config = {
       "configurable": {
           "thread_id": "user_pratik"
        }
    }

    user_input = input("Enter travel request: ")

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    print("\nFINAL RESPONSE:\n")

    for msg in result["messages"]:
        print(msg.content)

             
