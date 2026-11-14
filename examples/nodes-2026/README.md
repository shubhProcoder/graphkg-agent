# NODES 2026 Conference Example Dataset

This directory holds the sample knowledge graph data from the Neo4j NODES 2026 conference.

### Contents
- `data/*.csv`: Extracted entities, sessions, speakers, schedule slots, and vector embeddings.
- `data/load.cypher`: Batch loader script to populate Neo4j with all nodes, relationships, and vector indexes.
- `agent.json`: Preconfigured Aura Agent definition with Cypher templates and vector similarity search tools.

### Running with this dataset
Set `data.directory: examples/nodes-2026/data` in the root `config.yaml` to point to this dataset.

