# 🌍 Multi-Agent Travel System

An autonomous, multi-agent AI travel planning platform built with **LangGraph**, **Groq (Qwen/Llama)**, and **PostgreSQL**. The system coordinates specialized agents to search real-time flight schedules, curate hotel stays, generate day-by-day itineraries, and assemble complete trip packages within custom budgets.

**Live demo:** https://pratik-travel-planner.streamlit.app/

![Agent pipeline running](Screenshot%202026-09-13%20185451.png)

![Final travel plan](Screenshot%202026-09-13%20185506.png)

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

## 🛠️ Run it locally

```bash
git clone https://github.com/pratiksinghds/multi-agent-travel-system.git
cd multi-agent-travel-system
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```env
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
AVIATIONSTACK_API_KEY=your_aviationstack_key
# Optional: persist sessions in PostgreSQL. Without it, memory is kept in-process.
DATABASE_URL=postgresql://user:password@localhost:5432/travel
```

Start the app:

```bash
streamlit run frontend.py
```

You can also run the graph from the terminal with `python main.py`.

---

## 💡 Design notes

* **Airport codes from free text:** the flight agent asks the LLM for origin and destination IATA codes, then queries AviationStack with them, with a fallback when no codes are found.
* **Memory that works anywhere:** sessions are checkpointed in PostgreSQL when `DATABASE_URL` is set, and fall back to in-memory checkpoints on Streamlit Cloud.
* **Free-tier friendly:** output length is capped per agent so a full plan fits within Groq's free limits.
