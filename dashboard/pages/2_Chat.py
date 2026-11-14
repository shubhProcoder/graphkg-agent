"""
Chat Interface with the Knowledge Graph Agent.
"""

from __future__ import annotations
import sys
from pathlib import Path

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import re
import streamlit as st
import pandas as pd
from dashboard.components.db import get_config, run_query

config = get_config()

st.title("💬 Knowledge Graph AI Agent")
st.caption("Ask questions about sessions, speakers, schedule, or technologies in natural language.")

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"Hello! I am your {config.display_name} assistant. Ask me anything about the conference schedule, speakers, topics, or technologies.",
            "cypher": None,
            "data": None,
        }
    ]

# Example question prompts
st.markdown("**Suggested questions:**")
cols = st.columns(4)
sample_questions = [
    "Who is speaking about GraphRAG?",
    "Find sessions by Andreas Kollegger",
    "What talks mention LangChain?",
    "Which sessions are in Track 1?",
]

chosen_sample = None
for i, q in enumerate(sample_questions):
    with cols[i]:
        if st.button(q, key=f"sample_{i}", use_container_width=True):
            chosen_sample = q


def execute_agent_query(user_text: str) -> tuple[str, str, list[dict]]:
    """Determine the query strategy, execute it, and format the response."""
    cleaned = user_text.lower().strip()

    # Strategy 1: Check for speaker query
    speaker_patterns = [r"by ([\w\s]+)", r"speaker ([\w\s]+)", r"who is ([\w\s]+)"]
    speaker_match = None
    for p in speaker_patterns:
        m = re.search(p, cleaned)
        if m:
            speaker_match = m.group(1).replace("presenting", "").replace("speaking", "").strip()
            break

    if speaker_match and len(speaker_match) > 2:
        cypher = """
        MATCH (sp:Speaker)
        WHERE toLower(sp.name) CONTAINS toLower($name)
        MATCH (sp)-[:PRESENTS]->(s:Session)
        OPTIONAL MATCH (s)-[:HAS_SLOT]->(sl:Slot)
        WITH sp, s, sl ORDER BY sl.startTime
        WITH sp, s, collect(sl.displayTime) AS times
        RETURN sp.name AS speaker, s.title AS title, times
        ORDER BY speaker, title LIMIT 25
        """
        rows = run_query(cypher, {"name": speaker_match})
        if rows:
            reply = f"I found **{len(rows)}** session(s) associated with **{speaker_match.title()}**:"
        else:
            reply = f"No sessions found for speaker matching '{speaker_match}'."
        return reply, cypher, rows

    # Strategy 2: Check for topic, technology, or concept mention
    topic_patterns = [
        r"about ([\w\s\-\.]+)",
        r"mention ([\w\s\-\.]+)",
        r"talks on ([\w\s\-\.]+)",
        r"sessions on ([\w\s\-\.]+)",
    ]
    topic_match = None
    for p in topic_patterns:
        m = re.search(p, cleaned)
        if m:
            topic_match = m.group(1).replace("?", "").strip()
            break

    if topic_match and len(topic_match) > 2:
        cypher = """
        MATCH (s:Session)-[:HAS_TOPIC|HAS_USE_CASE|MENTIONS]->(x)
        WHERE toLower(x.name) CONTAINS toLower($name)
        WITH DISTINCT s
        OPTIONAL MATCH (s)<-[:PRESENTS]-(sp:Speaker)
        OPTIONAL MATCH (s)-[:HAS_SLOT]->(sl:Slot)
        WITH s, sp, sl ORDER BY sl.startTime
        WITH s, collect(DISTINCT sp.name) AS speakers,
             collect(DISTINCT sl.displayTime) AS times,
             min(sl.startTime) AS first
        RETURN s.title AS title, speakers, times
        ORDER BY first LIMIT 25
        """
        rows = run_query(cypher, {"name": topic_match})
        if rows:
            reply = f"Found **{len(rows)}** session(s) discussing **{topic_match.title()}**:"
        else:
            reply = f"No sessions explicitly tagged or mentioning '{topic_match}'."
        return reply, cypher, rows

    # Strategy 3: General keyword match across Session titles and descriptions
    words = [w for w in re.findall(r"\w+", cleaned) if len(w) > 3 and w not in ["what", "which", "show", "tell", "list", "sessions", "talks"]]
    search_keyword = words[0] if words else cleaned

    cypher = """
    MATCH (s:Session)
    WHERE toLower(s.title) CONTAINS toLower($kw)
       OR toLower(s.description) CONTAINS toLower($kw)
    OPTIONAL MATCH (s)<-[:PRESENTS]-(sp:Speaker)
    OPTIONAL MATCH (s)-[:HAS_SLOT]->(sl:Slot)
    WITH s, collect(DISTINCT sp.name) AS speakers, collect(DISTINCT sl.displayTime) AS times
    RETURN s.title AS title, speakers, times, substring(s.description, 0, 150) + '...' AS summary
    LIMIT 20
    """
    rows = run_query(cypher, {"kw": search_keyword})
    if rows:
        reply = f"Here are **{len(rows)}** session(s) matching your inquiry for *'{search_keyword}'*:"
    else:
        reply = f"I could not locate any sessions matching *'{search_keyword}'* in the graph."
    return reply, cypher, rows


# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("cypher"):
            with st.expander("Show Cypher Query"):
                st.code(msg["cypher"], language="cypher")
        if msg.get("data"):
            df = pd.DataFrame(msg["data"])
            st.dataframe(df, use_container_width=True)

# User input handling
user_input = st.chat_input("Ask a question about the conference...")
prompt = chosen_sample or user_input

if prompt:
    # Append user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process query
    with st.chat_message("assistant"):
        with st.spinner("Querying knowledge graph..."):
            reply, cypher, data = execute_agent_query(prompt)
            st.markdown(reply)
            if cypher:
                with st.expander("Show Cypher Query"):
                    st.code(cypher, language="cypher")
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply,
                "cypher": cypher,
                "data": data,
            })

