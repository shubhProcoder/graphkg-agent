"""
Knowledge Graph Schema & Ontology Inspector.
"""

from __future__ import annotations
import sys
from pathlib import Path

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import pandas as pd
from dashboard.components.db import get_config, run_query

config = get_config()

st.title("📋 Schema & Ontology Inspector")
st.caption("Inspect the active graph data model, node taxonomies, and database indexes.")

# Section 1: Node Definitions
st.subheader("🏷️ Configured Node Labels")
configured_nodes = config.raw.get("schema", {}).get("nodes", [])

# Fetch live counts from DB
live_node_counts = {}
try:
    rows = run_query("""
    MATCH (n)
    UNWIND labels(n) AS label
    WITH label, count(*) AS count
    RETURN label, count
    """)
    live_node_counts = {r["label"]: r["count"] for r in rows}
except Exception as e:
    st.warning(f"Could not fetch live node counts: {e}")

node_rows = []
for n in configured_nodes:
    lbl = n.get("label", "")
    node_rows.append({
        "Icon": n.get("icon", "⚪"),
        "Label": lbl,
        "Color": n.get("color", "#888888"),
        "Display Property": n.get("display_property", "name"),
        "Description": n.get("description", ""),
        "Live Instances": live_node_counts.get(lbl, 0),
    })

if node_rows:
    df_nodes = pd.DataFrame(node_rows)
    st.dataframe(
        df_nodes,
        column_config={
            "Color": st.column_config.TextColumn("Color Hex"),
            "Live Instances": st.column_config.NumberColumn("Database Count", format="%d"),
        },
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")

# Section 2: Relationship Definitions
st.subheader("🔗 Configured Relationships")
configured_rels = config.get_relationship_types()

live_rel_counts = {}
try:
    rows = run_query("MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count")
    live_rel_counts = {r["type"]: r["count"] for r in rows}
except Exception as e:
    st.warning(f"Could not fetch live relationship counts: {e}")

rel_rows = []
for r in configured_rels:
    rtype = r.get("type", "")
    rel_rows.append({
        "Type": rtype,
        "Source Node": r.get("from", "*"),
        "Target Node": r.get("to", "*"),
        "Description": r.get("description", ""),
        "Live Instances": live_rel_counts.get(rtype, 0),
    })

if rel_rows:
    df_rels = pd.DataFrame(rel_rows)
    st.dataframe(
        df_rels,
        column_config={
            "Live Instances": st.column_config.NumberColumn("Database Count", format="%d"),
        },
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")

# Section 3: Live Indexes & Constraints
st.subheader("⚡ Live Database Indexes & Constraints")
try:
    indexes = run_query("SHOW INDEXES YIELD name, type, entityType, labelsOrTypes, properties, state")
    if indexes:
        df_idx = pd.DataFrame(indexes)
        st.dataframe(df_idx, use_container_width=True, hide_index=True)
except Exception as e:
    st.caption(f"Index introspection not available: {e}")

# Raw YAML Config view
with st.expander("📄 View Active config.yaml"):
    st.json(config.raw)

