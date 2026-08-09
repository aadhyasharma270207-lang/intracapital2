# Intracapital Backend — Discovering Businesses Hidden Inside Enterprise Assets

**Intracapital** is an AI-powered Business Opportunity Discovery Platform. It analyzes a company's scattered internal enterprise assets (patents, sensor telemetry logs, customer feedback CSVs, product specifications, research papers, manufacturing IoT data, historical project records) to discover NEW, high-value business opportunities that the company can build using assets it already owns.

The system acts like an **AI Venture Capitalist / AI Co-Founder** with **100% local processing** and zero paid API dependencies.

---

## 🏛️ System Architecture

```text
                               ┌───────────────────────────────────┐
                               │            USER / UI              │
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                               ┌───────────────────────────────────┐
                               │           FASTAPI API             │
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                               ┌───────────────────────────────────┐
                               │       MULTI-FORMAT INGESTION      │
                               │  (PDF, DOCX, TXT, CSV, JSON, XLSX)│
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                               ┌───────────────────────────────────┐
                               │     CHUNK & EMBEDDING ENGINE      │
                               │    (sentence-transformers local)  │
                               └─────────┬─────────────────┬───────┘
                                         │                 │
                                         ▼                 ▼
                         ┌───────────────────────┐ ┌─────────────────────────┐
                         │      QDRANT (Vector)  │ │   NEO4J (Knowledge Graph)│
                         └───────────────┬───────┘ └───────────────┬─────────┘
                                         │                 │
                                         └────────┬────────┘
                                                  ▼
                               ┌───────────────────────────────────┐
                               │        RAG RETRIEVAL ENGINE       │
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                               ┌───────────────────────────────────┐
                               │    LANGGRAPH AGENT ORCHESTRATOR   │
                               │ ┌───────────────────────────────┐ │
                               │ │  Data Analysis Agent          │ │
                               │ │  Market Research Agent        │ │
                               │ │  Innovation Agent             │ │
                               │ │  Evaluation Agent             │ │
                               │ └───────────────────────────────┘ │
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                               ┌───────────────────────────────────┐
                               │      IBM GRANITE (via Ollama)     │
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                               ┌───────────────────────────────────┐
                               │    DETERMINISTIC SCORE & EXPLAIN  │
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                               ┌───────────────────────────────────┐
                               │      DISCOVERED OPPORTUNITIES     │
                               └───────────────────────────────────┘
```

---

## 🛠️ Required Technology Stack

- **Backend Framework**: Python 3.11+, FastAPI, Pydantic v2, Uvicorn
- **AI Core LLM**: IBM Granite (via local Ollama daemon)
- **Local Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Vector Database**: Qdrant (Self-hosted / Docker / Local with in-memory fallback)
- **Knowledge Graph**: Neo4j Community Edition (Bolt Cypher with in-memory fallback)
- **Agent Framework**: LangGraph
- **Database**: SQLite (SQLAlchemy ORM configured for PostgreSQL migration)
- **Testing**: pytest
- **Containerization**: Docker & Docker Compose

---

## 🚀 Quickstart & Setup

### 1. Clone & Environment Setup
```bash
cd intracapital2

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables (.env)
Create `.env` file from template:
```bash
cp .env.example .env
```

Default configuration in `.env`:
```env
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000

OLLAMA_BASE_URL=http://localhost:11434
GRANITE_MODEL=granite3.1-dense:8b

QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=enterprise_knowledge

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

DATABASE_URL=sqlite:///./intracapital.db
```

### 3. Local Services Setup (Ollama, Qdrant, Neo4j)

#### A. Install & Run Ollama with IBM Granite
```bash
# Install Ollama (Mac / Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull local IBM Granite model
ollama pull granite3.1-dense:8b
```

#### B. Run Vector DB & Graph DB via Docker Compose
```bash
docker-compose up -d qdrant neo4j
```

*(Note: If Neo4j or Qdrant daemons are not running, Intracapital automatically activates robust in-memory vector & knowledge graph engines so processing never halts.)*

---

## ⚡ Running the Backend

### Start FastAPI Server
```bash
PYTHONPATH=. .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger API documentation will be available at: [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🎯 Demo Dataset & End-to-End Discovery Walkthrough

The backend includes a realistic multi-format synthetic enterprise dataset in `demo_data/`:
1. `warehouse_sensor_report.txt` (SENSOR_DATA)
2. `logistics_cold_chain_report.txt` (HISTORICAL_PROJECT)
3. `customer_feedback.csv` (CUSTOMER_FEEDBACK)
4. `manufacturing_iot_log.json` (MANUFACTURING_LOG)
5. `patent_thermal_monitoring.txt` (PATENT)
6. `product_specs_hvac.txt` (PRODUCT)
7. `market_trends_research.json` (RESEARCH)

### 1. Seed Demo Dataset
```bash
PYTHONPATH=. .venv/bin/python -m scripts.seed_demo_data
```

### 2. Trigger Opportunity Discovery Pipeline
```bash
PYTHONPATH=. .venv/bin/python -m scripts.run_e2e_discovery
```

---

## 📊 Deterministic Opportunity Scoring Formula

The Evaluation Agent calculates overall opportunity scores from 0-100 using a strict deterministic formula:

$$\text{Overall Score} = 0.30 \cdot \text{Market Potential} + 0.25 \cdot \text{Feasibility} + 0.20 \cdot \text{Strategic Fit} + 0.15 \cdot \text{Asset Reusability} + 0.10 \cdot \text{Confidence}$$

---

## 📬 API Endpoint Documentation & Example cURL Requests

### 1. Health Check Endpoint
```bash
curl -X GET http://localhost:8000/health
```

### 2. Upload Document & Ingest Asset
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@demo_data/warehouse_sensor_report.txt" \
  -F "asset_type=SENSOR_DATA" \
  -F "company_name=Intracapital Corp"
```

### 3. List All Ingested Documents
```bash
curl -X GET http://localhost:8000/api/v1/documents
```

### 4. List Enterprise Assets
```bash
curl -X GET http://localhost:8000/api/v1/assets
```

### 5. Get Knowledge Graph Visualization Data
```bash
curl -X GET http://localhost:8000/api/v1/graph
```

### 6. Perform Vector RAG Search
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "thermal sensor logistics overheating",
    "top_k": 3
  }'
```

### 7. Trigger Opportunity Discovery
```bash
curl -X POST http://localhost:8000/api/v1/opportunities/discover \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Intracapital Corp"
  }'
```

### 8. List Discovered Opportunities
```bash
curl -X GET http://localhost:8000/api/v1/opportunities
```

### 9. Get Detailed Opportunity Explanation & Evidence
```bash
curl -X POST http://localhost:8000/api/v1/opportunities/OPP-001/explain
```

---

## 🧪 Running Unit & Integration Tests

Execute full test suite using `pytest`:
```bash
PYTHONPATH=. .venv/bin/pytest -v
```

---

## 🛡️ Privacy & Compliance Notice

Enterprise data processed by Intracapital remains **100% local**. No document text, embeddings, or metadata are transmitted to third-party SaaS APIs or external AI providers.
