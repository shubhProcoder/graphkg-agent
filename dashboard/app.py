"""
GraphKG Agent — Interactive Knowledge Graph Dashboard
Main application entry point.
"""

from __future__ import annotations
import sys
from pathlib import Path

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from dashboard.components.db import get_config, test_connection, run_query

config = get_config()

st.set_page_config(
    page_title=f"{config.display_name} | GraphKG",
    page_icon=config.icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #2d3342;
        text-align: center;
    }
    .metric-val {
        font-size: 2.2rem;
        font-weight: 700;
        color: #4C8BF5;
    }
    .metric-label {
        font-size: 0.95rem;
        color: #9aa5b1;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .hero-box {
        background: linear-gradient(135deg, #1b2838 0%, #151922 100%);
        border: 1px solid #29384d;
        border-radius: 12px;
        padding: 28px;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title(f"{config.icon} {config.project_name}")
st.sidebar.caption(config.description)

connected, conn_msg = test_connection()
if connected:
    st.sidebar.success("🟢 Neo4j Database Connected")
else:
    st.sidebar.error(f"🔴 Connection Failed: {conn_msg}")

st.sidebar.markdown("---")
st.sidebar.info("""
**GraphKG Agent Framework**  
Navigate pages via the menu above:
- **🔍 Explorer**: Interactive network visualization
- **💬 Chat**: Natural language KG query agent
- **📈 Analytics**: Graph stats and distributions
- **📋 Schema**: Active types & relations
""")

# Main Landing Hero
st.markdown(f"""
<div class="hero-box">
    <h1>{config.icon} {config.display_name}</h1>
    <p style="font-size: 1.15rem; color: #cbd5e1; max-width: 800px; margin-top: 10px;">
        {config.description}
    </p>
    <p style="font-size: 0.95rem; color: #94a3b8; margin-top: 5px;">
        Powered by <b>GraphKG Agent</b> — A config-driven Knowledge Graph framework combining Graph databases, Vector embeddings, and AI agents.
    </p>
</div>
""", unsafe_allow_html=True)

# Live Graph Metrics
if connected:
    try:
        node_count_res = run_query("MATCH (n) RETURN count(n) AS count")
        rel_count_res = run_query("MATCH ()-[r]->() RETURN count(r) AS count")
        labels_res = run_query("CALL db.labels() YIELD label RETURN count(label) AS count")
        rel_types_res = run_query("CALL db.relationshipTypes() YIELD relationshipType RETURN count(relationshipType) AS count")

        total_nodes = node_count_res[0]["count"] if node_count_res else 0
        total_rels = rel_count_res[0]["count"] if rel_count_res else 0
        total_labels = labels_res[0]["count"] if labels_res else 0
        total_types = rel_types_res[0]["count"] if rel_types_res else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{total_nodes:,}</div>
                <div class="metric-label">Graph Nodes</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{total_rels:,}</div>
                <div class="metric-label">Relationships</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{total_labels}</div>
                <div class="metric-label">Node Categories</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{total_types}</div>
                <div class="metric-label">Relation Types</div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"Could not load graph metrics: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# Feature Highlights Grid
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 🧭 Interactive Graph Explorer")
    st.write(
        "Visually inspect relationships, navigate interconnected entities, and zoom in on "
        "speakers, topics, tracks, and organizations using a force-directed network graph."
    )
    if st.button("Open Graph Explorer →", use_container_width=True):
        st.switch_page("pages/1_Explorer.py")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📈 Graph Analytics")
    st.write(
        "Explore distributions, top connected entities, multi-track breakdown, and "
        "technology adoption trends with interactive Plotly visualizations."
    )
    if st.button("Open Analytics →", use_container_width=True):
        st.switch_page("pages/3_Analytics.py")

with col_b:
    st.markdown("### 💬 AI Agent Chat")
    st.write(
        "Query the knowledge graph using natural language. The agent inspects your request, "
        "selects or generates targeted Cypher queries, and returns structured data."
    )
    if st.button("Open Chat Agent →", use_container_width=True):
        st.switch_page("pages/2_Chat.py")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📋 Schema & Taxonomy")
    st.write(
        "Inspect the configured graph ontology, node color legends, display properties, "
        "and live counts validated directly against the database."
    )
    if st.button("Inspect Schema →", use_container_width=True):
        st.switch_page("pages/4_Schema.py")

