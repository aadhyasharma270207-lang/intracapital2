from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class GraphNodeSchema(BaseModel):
    id: str
    labels: List[str]
    properties: Dict[str, Any]


class GraphEdgeSchema(BaseModel):
    from_node: str
    to_node: str
    type: str
    properties: Dict[str, Any] = {}


class FullGraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
