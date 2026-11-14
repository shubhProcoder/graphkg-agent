"""
Knowledge Graph Analytics & Visualizations.
"""

from __future__ import annotations
import sys
from pathlib import Path

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import plotly.express as px
import pandas as pd
from dashboard.components.db import get_config, run_query

config = get_config()

st.title("📈 Graph Analytics & Insights")
st.caption("Deep-dive metrics, entity distributions, and relationship structures.")

col1, col2 = st.columns(2)

# Chart 1: Node Distribution
with col1:
    st.subheader("📊 Entity Distribution")
    node_counts = run_query("""
    MATCH (n)
    UNWIND labels(n) AS label
    WITH label, count(*) AS count
    WHERE label <> '__Entity__' AND label <> 'Chunk'
    RETURN label, count
    ORDER BY count DESC
    """)
    if node_counts:
        df_nodes = pd.DataFrame(node_counts)
        fig_nodes = px.bar(
            df_nodes,
            x="label",
            y="count",
            color="label",
            title="Nodes by Label",
            labels={"label": "Node Label", "count": "Count"},
            template="plotly_dark",
        )
        fig_nodes.update_layout(showlegend=False, margin=dict(t=35, b=20, l=20, r=20))
        st.plotly_chart(fig_nodes, use_container_width=True)

# Chart 2: Relationship Distribution
with col2:
    st.subheader("🔗 Relationship Distribution")
    rel_counts = run_query("""
    MATCH ()-[r]->()
    RETURN type(r) AS type, count(*) AS count
    ORDER BY count DESC
    """)
    if rel_counts:
        df_rels = pd.DataFrame(rel_counts)
        fig_rels = px.bar(
            df_rels,
            x="type",
            y="count",
            color="type",
            title="Relationships by Type",
            labels={"type": "Relation Type", "count": "Count"},
            template="plotly_dark",
        )
        fig_rels.update_layout(showlegend=False, margin=dict(t=35, b=20, l=20, r=20))
        st.plotly_chart(fig_rels, use_container_width=True)

st.markdown("---")

col3, col4 = st.columns(2)

# Chart 3: Top Mentioned Technologies
with col3:
    st.subheader("⚙️ Top Mentioned Technologies")
    top_tech = run_query("""
    MATCH (s:Session)-[:MENTIONS]->(t:Technology)
    RETURN t.name AS technology, count(s) AS mentions
    ORDER BY mentions DESC
    LIMIT 10
    """)
    if top_tech:
        df_tech = pd.DataFrame(top_tech)
        fig_tech = px.bar(
            df_tech,
            x="mentions",
            y="technology",
            orientation="h",
            title="Top 10 Technologies in Sessions",
            labels={"mentions": "Session Mentions", "technology": "Technology"},
            template="plotly_dark",
            color="mentions",
            color_continuous_scale="Purples",
        )
        fig_tech.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=35, b=20, l=20, r=20))
        st.plotly_chart(fig_tech, use_container_width=True)

# Chart 4: Top Concepts
with col4:
    st.subheader("🧠 Top Mentioned Concepts")
    top_concepts = run_query("""
    MATCH (s:Session)-[:MENTIONS]->(c:Concept)
    RETURN c.name AS concept, count(s) AS mentions
    ORDER BY mentions DESC
    LIMIT 10
    """)
    if top_concepts:
        df_concepts = pd.DataFrame(top_concepts)
        fig_concept = px.bar(
            df_concepts,
            x="mentions",
            y="concept",
            orientation="h",
            title="Top 10 Central Concepts",
            labels={"mentions": "Mentions", "concept": "Concept"},
            template="plotly_dark",
            color="mentions",
            color_continuous_scale="Teal",
        )
        fig_concept.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=35, b=20, l=20, r=20))
        st.plotly_chart(fig_concept, use_container_width=True)

st.markdown("---")

col5, col6 = st.columns(2)

# Chart 5: Sessions per Track
with col5:
    st.subheader("🏷️ Sessions per Track")
    tracks = run_query("""
    MATCH (s:Session)-[:IN_TRACK]->(tr:Track)
    RETURN tr.name AS track, count(s) AS sessions
    ORDER BY sessions DESC
    """)
    if tracks:
        df_tracks = pd.DataFrame(tracks)
        fig_tracks = px.pie(
            df_tracks,
            names="track",
            values="sessions",
            title="Track Breakdown",
            template="plotly_dark",
            hole=0.4,
        )
        fig_tracks.update_layout(margin=dict(t=35, b=20, l=20, r=20))
        st.plotly_chart(fig_tracks, use_container_width=True)

# Chart 6: Most Connected Speakers
with col6:
    st.subheader("👥 Key Presenters")
    speakers = run_query("""
    MATCH (sp:Speaker)-[:PRESENTS]->(s:Session)
    RETURN sp.name AS speaker, count(s) AS sessions
    ORDER BY sessions DESC, speaker ASC
    LIMIT 10
    """)
    if speakers:
        df_speakers = pd.DataFrame(speakers)
        st.dataframe(
            df_speakers,
            column_config={
                "speaker": st.column_config.TextColumn("Speaker Name"),
                "sessions": st.column_config.ProgressColumn("Sessions Count", format="%d", min_value=0, max_value=max(df_speakers["sessions"])),
            },
            use_container_width=True,
            hide_index=True,
        )

