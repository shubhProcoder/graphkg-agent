"""
Query Engine for GraphKG Agent.
Provides high-level graph exploration, schema introspection, and Cypher query execution.
"""

from __future__ import annotations
import os
from typing import Any
import neo4j
from graphkg.config import GraphKGConfig


class QueryEngine:
    """Interface for executing Cypher queries and analyzing graph structure."""

    def __init__(self, config: GraphKGConfig, driver: neo4j.Driver | None = None, database: str = "neo4j") -> None:
        self.config = config
        self.database = database
        self._driver = driver
        self._owns_driver = False

    @classmethod
    def from_env(cls, config: GraphKGConfig) -> QueryEngine:
        """Create QueryEngine using environment variables (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)."""
        uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
        user = os.environ.get("NEO4J_USERNAME", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        database = os.environ.get("NEO4J_DATABASE", "neo4j")

        driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))
        instance = cls(config=config, driver=driver, database=database)
        instance._owns_driver = True
        return instance

    @property
    def driver(self) -> neo4j.Driver:
        if self._driver is None:
            raise RuntimeError("Driver not initialized.")
        return self._driver

    def close(self) -> None:
        """Close driver connection if created by this engine."""
        if self._owns_driver and self._driver:
            self._driver.close()

    def run_cypher(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Run a Cypher query and return results as a list of dictionaries."""
        with self.driver.session(database=self.database) as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]

    def get_node_counts(self) -> dict[str, int]:
        """Return counts of each node label in the graph."""
        query = """
        MATCH (n)
        UNWIND labels(n) AS label
        RETURN label, count(*) AS count
        ORDER BY count DESC
        """
        rows = self.run_cypher(query)
        return {r["label"]: r["count"] for r in rows}

    def get_relationship_counts(self) -> dict[str, int]:
        """Return counts of each relationship type in the graph."""
        query = """
        MATCH ()-[r]->()
        RETURN type(r) AS type, count(*) AS count
        ORDER BY count DESC
        """
        rows = self.run_cypher(query)
        return {r["type"]: r["count"] for r in rows}

    def get_sample_nodes(self, label: str, limit: int = 15) -> list[dict[str, Any]]:
        """Fetch sample nodes for a given label."""
        query = f"""
        MATCH (n:`{label}`)
        RETURN elementId(n) AS _id, properties(n) AS props, labels(n) AS labels
        LIMIT $limit
        """
        rows = self.run_cypher(query, {"limit": limit})
        results = []
        for r in rows:
            node_data = dict(r["props"])
            node_data["_id"] = r["_id"]
            node_data["_labels"] = r["labels"]
            results.append(node_data)
        return results

    def search_nodes(self, search_term: str, label: str | None = None, limit: int = 25) -> list[dict[str, Any]]:
        """Search nodes matching search_term in any string property."""
        where_clause = ""
        if label:
            label_clause = f":`{label}`"
        else:
            label_clause = ""

        query = f"""
        MATCH (n{label_clause})
        WHERE any(val IN [v IN [k IN keys(n) | n[k]] WHERE v IS :: STRING]
                  WHERE toLower(val) CONTAINS toLower($term))
        RETURN elementId(n) AS _id, properties(n) AS props, labels(n) AS labels
        LIMIT $limit
        """
        rows = self.run_cypher(query, {"term": search_term, "limit": limit})
        results = []
        for r in rows:
            node_data = dict(r["props"])
            node_data["_id"] = r["_id"]
            node_data["_labels"] = r["labels"]
            results.append(node_data)
        return results

    def get_top_connected(self, label: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        """Retrieve nodes with the highest degree (most relationships)."""
        label_filter = f":`{label}`" if label else ""
        query = f"""
        MATCH (n{label_filter})-[r]-()
        WITH n, count(r) AS degree
        RETURN elementId(n) AS _id,
               labels(n) AS labels,
               properties(n) AS props,
               degree
        ORDER BY degree DESC
        LIMIT $limit
        """
        rows = self.run_cypher(query, {"limit": limit})
        results = []
        for r in rows:
            props = dict(r["props"])
            props["_id"] = r["_id"]
            props["_labels"] = r["labels"]
            props["_degree"] = r["degree"]
            results.append(props)
        return results

    def get_neighbors(self, element_id: str, depth: int = 1) -> dict[str, list[dict[str, Any]]]:
        """Fetch 1-hop or 2-hop neighborhood of a given node for visualization."""
        query = """
        MATCH (n)-[r]-(m)
        WHERE elementId(n) = $id
        RETURN elementId(n) AS source_id,
               labels(n) AS source_labels,
               properties(n) AS source_props,
               type(r) AS rel_type,
               elementId(m) AS target_id,
               labels(m) AS target_labels,
               properties(m) AS target_props
        LIMIT 100
        """
        rows = self.run_cypher(query, {"id": element_id})

        nodes_dict: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, Any]] = []

        for r in rows:
            s_id = r["source_id"]
            t_id = r["target_id"]

            if s_id not in nodes_dict:
                nodes_dict[s_id] = {
                    "id": s_id,
                    "labels": r["source_labels"],
                    "props": dict(r["source_props"]),
                }
            if t_id not in nodes_dict:
                nodes_dict[t_id] = {
                    "id": t_id,
                    "labels": r["target_labels"],
                    "props": dict(r["target_props"]),
                }

            edges.append({
                "from": s_id,
                "to": t_id,
                "type": r["rel_type"],
            })

        return {
            "nodes": list(nodes_dict.values()),
            "edges": edges,
        }

    def get_schema_from_db(self) -> dict[str, Any]:
        """Introspect active constraints, labels, and relationships."""
        labels_query = "CALL db.labels() YIELD label RETURN label ORDER BY label"
        rels_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType"

        labels = [r["label"] for r in self.run_cypher(labels_query)]
        rels = [r["relationshipType"] for r in self.run_cypher(rels_query)]

        return {
            "labels": labels,
            "relationships": rels,
        }
