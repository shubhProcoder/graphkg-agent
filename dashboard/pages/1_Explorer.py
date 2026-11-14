"""
Interactive Knowledge Graph Explorer.
"""

from __future__ import annotations
import sys
from pathlib import Path

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import streamlit.components.v1 as components
from dashboard.components.db import get_config, run_query
from dashboard.components.graph_viz import render_graph
from dashboard.components.filters import node_type_filter, search_box, limit_slider

config = get_config()

st.title("🔍 Interactive Graph Explorer")
st.caption("Visually traverse nodes, inspect entity details, and explore connected neighborhoods.")

# Sidebar Controls
selected_labels = node_type_filter(config)
query_term = search_box("Search by name/title")
limit = limit_slider(default_val=45, max_val=150)

if not selected_labels:
    st.warning("Please select at least one node type in the sidebar to render the graph.")
    st.stop()

# Query graph nodes and edges
with st.spinner("Loading graph data..."):
    try:
        if query_term:
            cypher = """
            MATCH (n)
            WHERE any(l IN labels(n) WHERE l IN $labels)
              AND any(val IN [v IN [k IN keys(n) | n[k]] WHERE v IS :: STRING]
                       WHERE toLower(val) CONTAINS toLower($term))
            WITH n LIMIT $limit
            OPTIONAL MATCH (n)-[r]-(m)
            WHERE any(l IN labels(m) WHERE l IN $labels)
            RETURN elementId(n) AS s_id, labels(n) AS s_labels, properties(n) AS s_props,
                   type(r) AS rel_type,
                   elementId(m) AS t_id, labels(m) AS t_labels, properties(m) AS t_props
            """
            params = {"labels": selected_labels, "term": query_term, "limit": limit}
        else:
            cypher = """
            MATCH (n)
            WHERE any(l IN labels(n) WHERE l IN $labels)
            WITH n LIMIT $limit
            OPTIONAL MATCH (n)-[r]-(m)
            WHERE any(l IN labels(m) WHERE l IN $labels)
            RETURN elementId(n) AS s_id, labels(n) AS s_labels, properties(n) AS s_props,
                   type(r) AS rel_type,
                   elementId(m) AS t_id, labels(m) AS t_labels, properties(m) AS t_props
            """
            params = {"labels": selected_labels, "limit": limit}

        rows = run_query(cypher, params)

        nodes_dict: dict[str, dict] = {}
        edges: list[dict] = []

        for r in rows:
            s_id = r.get("s_id")
            if s_id and s_id not in nodes_dict:
                nodes_dict[s_id] = {
                    "id": s_id,
                    "labels": r.get("s_labels", []),
                    "props": dict(r.get("s_props", {})),
                }

            t_id = r.get("t_id")
            if t_id and t_id not in nodes_dict:
                nodes_dict[t_id] = {
                    "id": t_id,
                    "labels": r.get("t_labels", []),
                    "props": dict(r.get("t_props", {})),
                }

            if s_id and t_id and r.get("rel_type"):
                edges.append({
                    "from": s_id,
                    "to": t_id,
                    "type": r.get("rel_type"),
                })

        nodes_list = list(nodes_dict.values())

    except Exception as e:
        st.error(f"Error executing graph query: {e}")
        st.stop()

# Visualization
st.markdown(f"**Loaded {len(nodes_list)} nodes and {len(edges)} connections**")

if nodes_list:
    html_graph = render_graph(nodes_list, edges, config, height="680px")
    components.html(html_graph, height=700, scrolling=False)

    # Node Details Inspector
    st.markdown("---")
    st.subheader("🔬 Node Inspector")

    node_options = {}
    for n in nodes_list:
        lbl = n.get("labels", ["Node"])[0]
        disp_prop = config.get_node_display_property(lbl)
        name = n["props"].get(disp_prop) or n["props"].get("name") or n["props"].get("title") or n["id"]
        node_options[f"[{lbl}] {name}"] = n

    selected_node_label = st.selectbox("Inspect properties of a visible node:", list(node_options.keys()))
    if selected_node_label:
        node_info = node_options[selected_node_label]
        col1, col2 = st.columns([1, 1])

        with col1:
            st.write("**Node Metadata**")
            st.json({
                "ID": node_info["id"],
                "Labels": node_info["labels"],
                "Properties": {k: v for k, v in node_info["props"].items() if k != "embedding"}
            })

        with col2:
            st.write("**Connected Relations**")
            n_id = node_info["id"]
            incident_edges = [e for e in edges if e["from"] == n_id or e["to"] == n_id]
            if incident_edges:
                st.dataframe(incident_edges, use_container_width=True)
            else:
                st.caption("No visible edges for this node under current filters.")

else:
    st.info("No nodes match your filter criteria. Try selecting different types or clearing your search.")

