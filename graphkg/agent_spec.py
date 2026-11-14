"""
Agent Specification Generator for GraphKG Agent.
Translates config.yaml into agent definitions compatible with Neo4j Aura Agent and local agents.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from graphkg.config import GraphKGConfig


class AgentSpec:
    """Generates standardized agent definitions from configuration."""

    @staticmethod
    def from_config(config: GraphKGConfig) -> dict[str, Any]:
        """Generate full agent specification dictionary."""
        return {
            "name": config.project_name,
            "description": config.description,
            "system_prompt": config.get_system_prompt().strip(),
            "tools": AgentSpec.get_tools(config),
        }

    @staticmethod
    def get_tools(config: GraphKGConfig) -> list[dict[str, Any]]:
        """Extract and format tools defined in the configuration."""
        raw_tools = config.get_agent_tools()
        formatted = []

        for t in raw_tools:
            tool_type = t.get("type", "cypher_template")
            entry: dict[str, Any] = {
                "name": t.get("name", "tool"),
                "description": t.get("description", ""),
                "type": tool_type,
            }

            if tool_type in ("cypher_template", "cypherTemplate"):
                entry["type"] = "cypherTemplate"
                entry["config"] = {
                    "template": t.get("template", "").strip(),
                    "parameters": t.get("parameters", []),
                }
            elif tool_type in ("similarity_search", "similaritySearch"):
                entry["type"] = "similaritySearch"
                entry["config"] = {
                    "provider": t.get("provider", "openai"),
                    "model": t.get("model", "text-embedding-3-small"),
                    "index": t.get("index", "session_chunk_embeddings"),
                    "top_k": t.get("top_k", 5),
                }
            elif tool_type in ("text2cypher", "text_to_cypher"):
                entry["type"] = "text2cypher"
                entry["config"] = {}

            formatted.append(entry)

        return formatted

    @staticmethod
    def export_agent_json(config: GraphKGConfig, output_path: str | Path = "agent.json") -> Path:
        """Export agent specification to a JSON file."""
        spec = AgentSpec.from_config(config)
        out_file = Path(output_path)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2)
        return out_file
