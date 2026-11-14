# GraphKG Agent

A reusable, configuration-driven Knowledge Graph Agent framework with an interactive Streamlit dashboard.

Transform tabular datasets into interconnected knowledge graphs, query them with AI agents, and explore them through an interactive web interface.

---

## Key Features

- **Configuration-Driven**: Define schemas, node categories, relations, and agent tools inside a single `config.yaml`.
- **Interactive Graph Explorer**: Force-directed network visualization powered by Pyvis, featuring multi-type filtering, search, and neighborhood inspection.
- **Natural Language Chat Agent**: Hybrid query engine matching user questions to Cypher query templates and exploratory graph traversals.
- **Analytics & Taxonomy**: Live distribution charts (Plotly), top-connected entity ranking, track breakdowns, and schema validation.
- **Multi-Backend Support**: Connect to managed cloud instances (Neo4j Aura) or local embedded graph engines.

---

## Project Structure

```
graphkg-agent/
├── config.yaml               # Active configuration (schemas, tools, datasets)
├── pyproject.toml            # Project dependencies and packaging
├── graphkg/                  # Core reusable Python framework
│   ├── __init__.py           # Package exports
│   ├── config.py             # YAML configuration loader & validator
│   ├── query_engine.py       # High-level Cypher execution & graph operations
│   ├── graph_loader.py       # Cypher and dataset ingestion helpers
│   └── agent_spec.py         # Agent JSON specification generator
├── dashboard/                # Streamlit web application
│   ├── app.py                # Main application dashboard
│   ├── components/
│   │   ├── db.py             # Database connection & query caching
│   │   ├── filters.py        # UI controls for labels, search, and limits
│   │   └── graph_viz.py      # Pyvis network graph renderer
│   └── pages/
│       ├── 1_Explorer.py     # Interactive visual graph explorer
│       ├── 2_Chat.py         # Knowledge graph chat agent
│       ├── 3_Analytics.py    # Plotly statistical dashboards
│       └── 4_Schema.py       # Live schema and constraint inspector
└── examples/
    └── nodes-2026/           # Conference schedule example dataset
        ├── config.yaml       # Example configuration
        ├── agent.json        # Pre-built agent tools definition
        └── data/             # CSV files & Cypher loader script
```

---

## Quickstart

### 1. Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (or pip)
- A Neo4j database instance (e.g. Neo4j Aura Free or local Neo4j)

### 2. Configure Environment
Create a `.env` file in the project root:
```env
NEO4J_URI=neo4j+s://<your-instance-id>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<your-instance-password>
NEO4J_DATABASE=neo4j
```

### 3. Install Dependencies
Using `uv`:
```bash
uv pip install -e .
```
Or using standard `pip`:
```bash
pip install -e .
```

### 4. Run the Dashboard
```bash
streamlit run dashboard/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Dashboard Pages

1. **Dashboard Home**: High-level graph counts (nodes, relationships, labels), health status, and architecture overview.
2. **Explorer**: Force-directed network graph. Filter visible node types, search by name or property, and inspect connected neighborhoods.
3. **Chat Agent**: Conversational agent providing answers grounded directly in the graph with inspectable Cypher queries.
4. **Analytics**: Statistical charts detailing node distributions, top mentioned technologies/concepts, and key contributors.
5. **Schema**: Overview of the active ontology and live database constraints/indexes.

---

## Adapting to Your Own Dataset

To use GraphKG Agent with your own custom dataset:

1. **Place your data**: Add your CSV or tabular data files to a new directory (e.g. `data/my-project/`).
2. **Update `config.yaml`**:
   - Set `project.name` and `project.display_name`.
   - Map your node types and properties under `schema.nodes`.
   - Define relationship rules under `schema.relationships`.
   - Configure agent query templates under `agent.tools`.
3. **Ingest data**: Load your data into Neo4j using Cypher or `graphkg.graph_loader.GraphLoader`.
4. **Launch**: Run `streamlit run dashboard/app.py` to explore your new knowledge graph.
