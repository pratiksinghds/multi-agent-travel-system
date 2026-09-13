import os
import streamlit as st
from langchain_core.messages import HumanMessage
from main import app

# --- Page Setup ---
st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon="✈️",
    layout="wide"
)

# --- Sidebar Details ---
with st.sidebar:
    st.header("🤖 AI Travel Booking System")
    st.markdown("### Agent Pipeline")
    st.markdown("""
    * **Flight Agent**: Real-time flight search
    * **Hotel Agent**: Best hotel recommendations
    * **Itinerary Agent**: Day-wise travel schedule
    * **Final Agent**: Synthesizes and summarizes
    """)

    st.markdown("---")
    st.markdown("### Technologies Used")
    st.markdown("""
    * **LangGraph** (StateGraph & Workflow)
    * **Groq** (Llama / Qwen LLMs)
    * **PostgreSQL** (Persistent Memory)
    * **Tavily Search API**
    * **AviationStack API**
    """)

    thread_id = st.text_input("Thread ID (Memory Session):", value="user_pratik")

# --- Header Section ---
st.title("✈️ AI Travel Booking System")
st.write("An intelligent Multi-Agent AI system that designs full travel itineraries with flights, accommodations, and sightseeing.")

# --- Destination Showcase Cards / Images ---
st.subheader("Popular Destinations")
img_col1, img_col2, img_col3 = st.columns(3)

with img_col1:
    st.image(
        "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=700&q=80",
        caption="Tokyo, Japan",
        use_container_width=True
    )

with img_col2:
    st.image(
        "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=700&q=80",
        caption="Kyoto, Japan",
        use_container_width=True
    )

with img_col3:
    st.image(
        "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?auto=format&fit=crop&w=700&q=80",
        caption="Mount Fuji, Japan",
        use_container_width=True
    )

st.markdown("---")

# --- Query Form ---
default_prompt = "Plan a complete 7 days Japan trip including flights, hotels and sightseeing under 2 lakh"
user_prompt = st.text_area("Enter your travel requirement:", value=default_prompt, height=90)

generate_btn = st.button("Generate My Travel Plan", type="primary", use_container_width=True)

# --- Graph Stream & Results ---
if generate_btn:
    if not user_prompt.strip():
        st.warning("Please enter your travel details.")
    else:
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {
            "messages": [HumanMessage(content=user_prompt)],
            "user_query": user_prompt,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        }

        st.subheader("Agent Pipeline Execution")
        status_box = st.empty()
        status_box.info("Starting agents...")

        node_outputs = {}

        # Stream node execution updates in real time
        with st.spinner("Processing workflow across all agents..."):
            for step in app.stream(initial_state, config=config):
                for node_name, state_values in step.items():
                    status_box.info(f"⚡ Executed: **{node_name}**")
                    node_outputs[node_name] = state_values

        status_box.success("✅ Travel plan successfully generated!")

        # --- Display Intermediate Agent Results ---
        tab1, tab2, tab3 = st.tabs(["✈️ Flights", "🏨 Hotels", "🗓️ Itinerary"])

        with tab1:
            flights = node_outputs.get("flight_agent", {}).get("flight_results", "No flight data available.")
            st.markdown(flights)

        with tab2:
            hotels = node_outputs.get("hotel_agent", {}).get("hotel_results", "No hotel data available.")
            st.markdown(hotels)

        with tab3:
            itin = node_outputs.get("itinerary_agent", {}).get("itinerary", "No itinerary generated.")
            st.markdown(itin)

        st.markdown("---")

        # --- Execution Analytics ---
        total_calls = node_outputs.get("final_agent", {}).get("llm_calls", 4)
        stat1, stat2, stat3 = st.columns(3)
        stat1.metric(label="Active Agents", value="4")
        stat2.metric(label="LLM Calls Tracked", value=str(total_calls))
        stat3.metric(label="Checkpointer State", value="Persisted in Postgres")

        # --- Final Generated Travel Plan ---
        st.subheader("📋 Final Travel Plan")
        final_text = ""
        if "final_agent" in node_outputs and "messages" in node_outputs["final_agent"]:
            final_text = node_outputs["final_agent"]["messages"][-1].content
        else:
            final_text = "Check state output for plan text."

        st.markdown(final_text)

        # --- Download Button ---
        st.download_button(
            label="Download Travel Plan",
            data=final_text,
            file_name="travel_itinerary.txt",
            mime="text/plain",
            use_container_width=True
        )