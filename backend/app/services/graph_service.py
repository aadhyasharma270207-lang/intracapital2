import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)

class GraphService:
    _driver = None
    _is_fallback: bool = False
    
    # Local fallback graph storage (in-memory, rebuilt during demo ingestion)
    _mock_nodes: Dict[str, Dict[str, Any]] = {}
    _mock_relationships: List[Dict[str, Any]] = []

    @classmethod
    def get_driver(cls):
        """
        Retrieves or initializes the Neo4j driver.
        Falls back to in-memory graph emulation if connection fails.
        """
        if cls._driver is not None:
            return cls._driver
            
        if cls._is_fallback:
            return None

        try:
            # Attempt to create driver and verify connection
            driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
            )
            driver.verify_connectivity()
            cls._driver = driver
            cls._is_fallback = False
            logger.info(f"Connected to Neo4j knowledge graph at {settings.NEO4J_URI}")
            return cls._driver
        except Exception as e:
            logger.warning(f"Could not connect to Neo4j at {settings.NEO4J_URI}: {str(e)}. Using in-memory graph emulator.")
            cls._is_fallback = True
            cls._driver = None
            return None

    @classmethod
    def check_status(cls) -> Dict[str, Any]:
        """
        Returns Neo4j service health status.
        """
        driver = cls.get_driver()
        if cls._is_fallback or driver is None:
            return {
                "status": "DEGRADED",
                "message": "Neo4j connection failed. Operating in local graph simulation mode.",
                "details": {"type": "in-memory-simulation"}
            }
        else:
            return {
                "status": "ONLINE",
                "message": "Connected to Neo4j knowledge graph database.",
                "details": {"uri": settings.NEO4J_URI}
            }

    @classmethod
    def add_node(cls, node_id: str, label: str, properties: Dict[str, Any]):
        """
        Add a node to the graph database.
        """
        driver = cls.get_driver()
        if driver is None:
            # Store in local memory simulation
            cls._mock_nodes[node_id] = {
                "id": node_id,
                "label": label,
                "properties": properties
            }
            return

        query = f"MERGE (n:{label} {{id: $id}}) SET n += $props"
        try:
            with driver.session() as session:
                session.run(query, id=node_id, props=properties)
        except Exception as e:
            logger.error(f"Neo4j failed to add node {node_id}: {str(e)}. Adding to emulator.")
            cls._mock_nodes[node_id] = {
                "id": node_id,
                "label": label,
                "properties": properties
            }

    @classmethod
    def add_relationship(cls, source_id: str, target_id: str, rel_type: str, properties: Optional[Dict[str, Any]] = None):
        """
        Create a directed relationship between two nodes.
        """
        properties = properties or {}
        driver = cls.get_driver()
        if driver is None:
            # Store in local memory simulation
            cls._mock_relationships.append({
                "source": source_id,
                "target": target_id,
                "type": rel_type,
                "properties": properties
            })
            return

        # Double check both nodes exist or merge
        query = (
            "MATCH (a {id: $source_id}), (b {id: $target_id}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            "SET r += $props"
        )
        try:
            with driver.session() as session:
                session.run(query, source_id=source_id, target_id=target_id, props=properties)
        except Exception as e:
            logger.error(f"Neo4j failed to create relationship: {str(e)}. Adding to emulator.")
            cls._mock_relationships.append({
                "source": source_id,
                "target": target_id,
                "type": rel_type,
                "properties": properties
            })

    @classmethod
    def get_entire_graph(cls) -> Dict[str, Any]:
        """
        Fetch the entire graph representation for visualization.
        Format: { "nodes": [ {id, label, properties} ], "edges": [ {source, target, type} ] }
        """
        driver = cls.get_driver()
        if driver is None:
            return {
                "nodes": list(cls._mock_nodes.values()),
                "edges": cls._mock_relationships
            }

        query = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 500"
        try:
            with driver.session() as session:
                result = session.run(query)
                nodes = {}
                edges = []
                for record in result:
                    n = record["n"]
                    m = record["m"]
                    r = record["r"]
                    
                    # Track nodes uniquely
                    for node in [n, m]:
                        n_id = node.get("id")
                        if n_id and n_id not in nodes:
                            labels = list(node.labels)
                            nodes[n_id] = {
                                "id": n_id,
                                "label": labels[0] if labels else "Unknown",
                                "properties": dict(node)
                            }
                            
                    edges.append({
                        "source": n.get("id"),
                        "target": m.get("id"),
                        "type": r.type,
                        "properties": dict(r)
                    })
                return {
                    "nodes": list(nodes.values()),
                    "edges": edges
                }
        except Exception as e:
            logger.error(f"Neo4j graph query failed: {str(e)}. Returning emulation data.")
            return {
                "nodes": list(cls._mock_nodes.values()),
                "edges": cls._mock_relationships
            }

    @classmethod
    def clear_graph(cls):
        """
        Clears all nodes and relationships.
        """
        cls._mock_nodes.clear()
        cls._mock_relationships.clear()
        driver = cls.get_driver()
        if driver is not None:
            try:
                with driver.session() as session:
                    session.run("MATCH (n) DETACH DELETE n")
            except Exception as e:
                logger.error(f"Failed to clear Neo4j graph: {str(e)}")
