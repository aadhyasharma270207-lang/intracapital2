# INTRACAPITAL Backend - AI Venture Intelligence

Backend engine for **INTRACAPITAL**, an AI Business Opportunity Discovery Platform that parses internal enterprise assets and extracts business opportunities using local LLM inference, vector spaces, and knowledge graphs.

## Technology Stack
- **FastAPI / Uvicorn**: REST API framework
- **Pydantic**: Data schema validation
- **SQLAlchemy & SQLite**: Workspace, Asset, Opportunity database registry
- **sentence-transformers**: Local 384-dimensional vector embeddings
- **qdrant-client**: Local Qdrant collections manager (with `:memory:` fallback)
- **neo4j**: Knowledge Graph query driver (with local SQLite/dict emulated fallback)
- **Docling / PyMuPDF / Pandas**: Multi-format document parser

---

## Offline-First & Resilient Fallbacks
This application is designed to be completely run locally by hackathon judges without configure internet or external API keys:
1. **Ollama / IBM Granite**: Checks `http://localhost:11434/api/tags` at startup. If Ollama is offline or `granite3-dense:8b` is not loaded, it falls back to a high-fidelity mock compiler that returns the requested demo opportunities for *FrostLink Logistics* (Cold Chain Intelligence, Predictive Maintenance, Route Optimization).
2. **Vector DB (Qdrant)**: If Docker is offline, it instantiates Qdrant Client in-memory (`location=":memory:"`).
3. **Knowledge Graph (Neo4j)**: If Neo4j is offline, it emulates graph connectivity in-memory to build nodes and relations.
4. **Parsers (Docling)**: If system dependencies or PyTorch are missing, it falls back to PyMuPDF, python-docx, and pandas to parse PDF, Word, and Excel files.

---

## Getting Started

### 1. Requirements Installation
Ensure Python 3.11+ is installed, then run:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Running Local Services (Optional)
If you want to use the live system integrations, make sure Ollama, Qdrant, and Neo4j are running.
Pull the IBM Granite model in Ollama:
```bash
ollama pull granite3-dense:8b
```

### 3. Start Backend
Run the backend web server:
```bash
uvicorn app.main:app --reload --port 8000
```
- API Endpoint: `http://localhost:8000/api/health`
- Interactive Documentation: `http://localhost:8000/docs`

### 4. Running Tests
Verify backend health and database schema creation using pytest:
```bash
python -m pytest
```

---

## API Routes Documentation
- **Health / System**: `GET /api/health`, `GET /api/system/status`
- **Asset Upload**: `POST /api/assets/upload`, `GET /api/assets`, `DELETE /api/assets/{id}`
- **Discovery**: `POST /api/discovery/start`, `GET /api/discovery/{job_id}`
- **Opportunities**: `GET /api/opportunities`, `GET /api/opportunities/{id}`
- **Evidence Explorer**: `GET /api/opportunities/{id}/evidence`
- **Business Model Canvas**: `GET /api/opportunities/{id}/business-model`
- **Human Review**: `POST /api/opportunities/{id}/validate`
- **Compare Matrix**: `POST /api/opportunities/compare`
- **Demo Load**: `POST /api/demo/load` (populates FrostLink Logistics)
