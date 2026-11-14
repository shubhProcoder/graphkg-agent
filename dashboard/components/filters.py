"""
Sidebar and filter UI components for the dashboard.
"""

from __future__ import annotations
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from graphkg.config import GraphKGConfig


def node_type_filter(config: GraphKGConfig, default_selected: list[str] | None = None) -> list[str]:
    """Render checkboxes or multiselect for node labels in sidebar."""
    all_labels = config.get_node_labels()
    if default_selected is None:
        # Pick top representative labels by default
        default_selected = [l for l in ["Session", "Speaker", "Technology", "Topic"] if l in all_labels]
        if not default_selected:
            default_selected = all_labels[:4]

    st.sidebar.subheader("Filter Node Types")
    selected = st.sidebar.multiselect(
        "Select types to display:",
        options=all_labels,
        default=default_selected,
        help="Filter visible node categories in the graph",
    )
    return selected


def search_box(label: str = "Search graph nodes") -> str:
    """Render search input in sidebar or main area."""
    return st.sidebar.text_input("🔍 " + label, placeholder="e.g. LangChain, GraphRAG, Eifrem").strip()


def limit_slider(default_val: int = 40, max_val: int = 150) -> int:
    """Render a slider for node limit."""
    return st.sidebar.slider(
        "Max nodes to display",
        min_value=10,
        max_value=max_val,
        value=default_val,
        step=10,
    )
