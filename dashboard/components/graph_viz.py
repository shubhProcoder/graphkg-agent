"""
Pyvis Network graph renderer for interactive Streamlit visualization.
"""

from __future__ import annotations
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import json
from typing import Any
from pyvis.network import Network
from graphkg.config import GraphKGConfig


def render_graph(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    config: GraphKGConfig,
    height: str = "650px",
    width: str = "100%",
) -> str:
    """Build a Pyvis Network and return the generated HTML string."""
    net = Network(height=height, width=width, bgcolor="#0e1117", font_color="#ffffff", directed=True)

    added_nodes = set()

    for n in nodes:
        node_id = str(n.get("id"))
        if node_id in added_nodes:
            continue
        added_nodes.add(node_id)

        labels = n.get("labels", [])
        primary_label = labels[0] if labels else "Node"
        props = n.get("props", {})

        color = config.get_node_color(primary_label)
        display_prop = config.get_node_display_property(primary_label)
        label_text = str(props.get(display_prop) or props.get("name") or props.get("title") or primary_label)
        if len(label_text) > 28:
            label_text = label_text[:25] + "..."

        # Format hover tooltip
        tooltip_lines = [f"<b>Type:</b> {primary_label}"]
        for k, v in list(props.items())[:8]:
            if k == "embedding":
                continue
            val_str = str(v)
            if len(val_str) > 60:
                val_str = val_str[:57] + "..."
            tooltip_lines.append(f"<b>{k}:</b> {val_str}")
        tooltip = "<br>".join(tooltip_lines)

        net.add_node(
            node_id,
            label=label_text,
            title=tooltip,
            color=color,
            shape="dot",
            size=18,
            borderWidth=2,
            shadow=True,
        )

    for e in edges:
        s = str(e.get("from"))
        t = str(e.get("to"))
        rel_type = str(e.get("type", ""))

        if s in added_nodes and t in added_nodes:
            net.add_edge(
                s,
                t,
                title=rel_type,
                label=rel_type,
                color={"color": "#6c757d", "highlight": "#ffc107"},
                arrows="to",
                font={"size": 10, "color": "#a0aab2", "align": "middle"},
                smooth={"type": "continuous"},
            )

    # Set physics layout options
    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {"iterations": 150}
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true
      }
    }
    """)

    return net.generate_html()
