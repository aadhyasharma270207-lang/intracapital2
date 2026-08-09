# INTRACAPITAL - AI Venture Intelligence

> Discover Businesses Hidden Inside Businesses.

INTRACAPITAL is an AI-powered Business Opportunity Discovery Platform built for the IBM HackVerse 2.0 hackathon. It parses unstructured enterprise files, extracts database signals, connects ideas using local vector databases (Qdrant) and knowledge graphs (Neo4j), and leverages IBM Granite 4.x (via Ollama) to autonomously generate, score, and validator new venture ideas.

---

## 1. Local Containerized Orchestration

To run the complete INTRACAPITAL infrastructure (FastAPI, Qdrant, Neo4j, Ollama) using Docker, execute:

### Deploy Services
```bash
docker compose up -d
```

### Verify Container Status
Check that all services are online and mapped correctly:
```bash
docker compose ps
```

### Check Logs
```bash
docker compose logs -f backend
```

---

## 2. Local Ollama & IBM Granite Model Pulling

Since downloading large model weights (IBM Granite is ~4.9GB) shouldn't be automated during compose initialization, you must pull the model manually inside the running Ollama container:

```bash
docker compose exec ollama ollama pull granite3-dense:8b
```
*(Alternatively, if running Ollama natively on Windows, run `ollama pull granite3-dense:8b` in your local terminal).*

---

## 3. Environment Variables Configuration

Create a `.env` in the root workspace (copied from `.env.example`):
```ini
# Configures the Granite model to load
GRANITE_MODEL=granite3-dense:8b

# Credentials for Neo4j Community database container
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123

# Direct CORS access whitelist
FRONTEND_URL=http://localhost:5173
```

---

## 4. Port Allocations
- **FastAPI Backend Gateway**: `http://localhost:8000` (Swagger: `http://localhost:8000/docs`)
- **Qdrant Vector DB Dashboard**: `http://localhost:6333/dashboard`
- **Neo4j Graph Dashboard**: `http://localhost:7474`
- **Ollama LLM Engine API**: `http://localhost:11434`
