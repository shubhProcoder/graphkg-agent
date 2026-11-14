"""
Configuration management for GraphKG Agent.
Loads and validates YAML configuration files defining schemas, data sources, and agents.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Any
import yaml


class GraphKGConfig:
    """Manages project configuration loaded from config.yaml."""

    def __init__(self, data: dict[str, Any], config_path: Path | None = None) -> None:
        self._data = data
        self._config_path = config_path or Path.cwd() / "config.yaml"

    @classmethod
    def load(cls, path: str | Path = "config.yaml") -> GraphKGConfig:
        """Load configuration from a YAML file."""
        config_file = Path(path).resolve()
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls(data, config_file)

    @property
    def raw(self) -> dict[str, Any]:
        """Access raw config dictionary."""
        return self._data

    @property
    def project_name(self) -> str:
        return self._data.get("project", {}).get("name", "knowledge-graph")

    @property
    def display_name(self) -> str:
        return self._data.get("project", {}).get("display_name", "Knowledge Graph Explorer")

    @property
    def description(self) -> str:
        return self._data.get("project", {}).get("description", "")

    @property
    def icon(self) -> str:
        return self._data.get("project", {}).get("icon", "🕸️")

    def get_data_dir(self) -> Path:
        """Resolve the data directory path relative to the config file or cwd."""
        raw_dir = self._data.get("data", {}).get("directory", "data")
        candidate = Path(raw_dir)
        if candidate.is_absolute():
            return candidate
        base_dir = self._config_path.parent
        return (base_dir / candidate).resolve()

    def get_node_labels(self) -> list[str]:
        """List of all configured node labels."""
        nodes = self._data.get("schema", {}).get("nodes", [])
        return [n["label"] for n in nodes if "label" in n]

    def get_node_config(self, label: str) -> dict[str, Any]:
        """Get schema details for a specific node label."""
        nodes = self._data.get("schema", {}).get("nodes", [])
        for n in nodes:
            if n.get("label") == label:
                return n
        # Default fallback
        return {
            "label": label,
            "display_property": "name",
            "color": "#888888",
            "icon": "⚪",
            "description": f"Node of type {label}",
        }

    def get_node_color(self, label: str) -> str:
        """Get color associated with a node label."""
        return self.get_node_config(label).get("color", "#4C8BF5")

    def get_node_display_property(self, label: str) -> str:
        """Get the primary property used for display (e.g. title, name)."""
        return self.get_node_config(label).get("display_property", "name")

    def get_relationship_types(self) -> list[dict[str, Any]]:
        """List of configured relationship schemas."""
        return self._data.get("schema", {}).get("relationships", [])

    def get_agent_tools(self) -> list[dict[str, Any]]:
        """List of configured agent tools (cypher templates, similarity search, etc)."""
        return self._data.get("agent", {}).get("tools", [])

    def get_system_prompt(self) -> str:
        """Get agent system prompt."""
        return self._data.get("agent", {}).get("system_prompt", "You are a helpful knowledge graph assistant.")

    def get_schema_description(self) -> str:
        """Build a human-readable schema description suitable for LLMs."""
        rels = self.get_relationship_types()
        rel_strs = []
        for r in rels:
            src = r.get("from", "Node")
            tgt = r.get("to", "Node")
            rtype = r.get("type", "RELATED_TO")
            rel_strs.append(f"(:{src})-[:{rtype}]->(:{tgt})")

        nodes = self.get_node_labels()
        return (
            f"Knowledge Graph Nodes: {', '.join(nodes)}.\n"
            f"Relationships: {', '.join(rel_strs)}."
        )
