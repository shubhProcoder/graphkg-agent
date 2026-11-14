"""
Graph Loader for GraphKG Agent.
Loads data and schemas into Neo4j or Relate.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Any
import neo4j


class GraphLoader:
    """Utilities for loading Cypher scripts and CSV data into graph databases."""

    def __init__(self, driver: neo4j.Driver, database: str = "neo4j") -> None:
        self.driver = driver
        self.database = database

    @classmethod
    def from_env(cls) -> GraphLoader:
        uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
        user = os.environ.get("NEO4J_USERNAME", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        database = os.environ.get("NEO4J_DATABASE", "neo4j")

        driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))
        return cls(driver=driver, database=database)

    def load_from_cypher(self, cypher_file_path: str | Path) -> list[str]:
        """Execute a .cypher script containing semicolon-separated statements."""
        path = Path(cypher_file_path)
        if not path.exists():
            raise FileNotFoundError(f"Cypher file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split into distinct statements by semicolon at end of lines
        raw_statements = [s.strip() for s in content.split(";") if s.strip()]
        executed = []

        with self.driver.session(database=self.database) as session:
            for stmt in raw_statements:
                # Skip comments-only blocks
                clean_lines = [l for l in stmt.splitlines() if not l.strip().startswith("//")]
                if not "".join(clean_lines).strip():
                    continue
                session.run(stmt)
                executed.append(stmt[:60] + "...")

        return executed
