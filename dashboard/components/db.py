"""
Database helper and connection manager for the Streamlit dashboard.
"""

from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import neo4j
from dotenv import load_dotenv
from graphkg.config import GraphKGConfig

# Load environment variables from .env
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)


@st.cache_resource
def get_config() -> GraphKGConfig:
    """Load and cache the global configuration."""
    cfg_path = Path(__file__).resolve().parent.parent.parent / "config.yaml"
    return GraphKGConfig.load(cfg_path)


@st.cache_resource
def get_driver() -> neo4j.Driver:
    """Initialize and cache the Neo4j driver connection."""
    uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    username = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "password")

    return neo4j.GraphDatabase.driver(uri, auth=(username, password))


def get_database_name() -> str:
    return os.environ.get("NEO4J_DATABASE", "neo4j")


def run_query(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Execute Cypher query and return list of row dictionaries."""
    driver = get_driver()
    db_name = get_database_name()
    with driver.session(database=db_name) as session:
        result = session.run(query, params or {})
        return [dict(record) for record in result]


def test_connection() -> tuple[bool, str]:
    """Test connectivity to Neo4j instance."""
    try:
        rows = run_query("RETURN 1 AS ping")
        if rows and rows[0].get("ping") == 1:
            return True, "Connected successfully"
        return False, "Query returned unexpected result"
    except Exception as e:
        return False, str(e)
