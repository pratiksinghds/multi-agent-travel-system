# 🌍 Multi-Agent Travel System

An autonomous, multi-agent AI travel planning platform built with **LangGraph**, **Groq (Qwen/Llama)**, and **PostgreSQL**. The system coordinates specialized agents to search real-time flight schedules, curate hotel stays, generate day-by-day itineraries, and assemble complete trip packages within custom budgets.

---

## 🏗️ System Architecture

The graph workflow orchestrates four discrete agents with persistent PostgreSQL checkpointing:

1. **✈️ Flight Agent**: Queries real-time flight routes via AviationStack API.
2. **🏨 Hotel Agent**: Retrieves and filters lodging recommendations via Tavily Search API.
3. **🗓️ Itinerary Agent**: Plans day-by-day sightseeing and scheduling.
4. **📝 Final Agent**: Synthesizes intermediate agent findings into a structured, downloadable itinerary.

---

## 🚀 Tech Stack

* **Orchestration**: LangGraph (StateGraph)
* **LLM**: Groq API (`qwen/qwen3.8-27b`)
* **State & Memory Checkpointing**: PostgreSQL via `psycopg`
* **External APIs**: Tavily Web Search API, AviationStack API
* **Frontend**: Streamlit

---

## 🛠️ Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/](https://github.com/)pratiksinghds/multi-agent-travel-system.git
cd multi-agent-travel-system
