from pydantic import BaseModel


class HealthResponse(BaseModel):
    api: str = "ok"
    ollama: str
    neo4j: str
    qdrant: str
