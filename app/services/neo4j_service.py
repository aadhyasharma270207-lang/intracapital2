from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from app.config import settings
from app.utils.logger import logger


class Neo4jService:
    def __init__(self):
        self.is_connected = False
        self.driver = None
        self._memory_nodes: Dict[str, Dict[str, Any]] = {}
        self._memory_edges: List[Dict[str, Any]] = []

        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
            )
            # Verify connectivity
            self.driver.verify_connectivity()
            self.is_connected = True
            logger.info(f"[NEO4J] Connected to Neo4j database at {settings.NEO4J_URI}")
        except Exception as e:
            logger.warning(f"[NEO4J] Could not connect to Neo4j instance ({e}). Using robust local in-memory knowledge graph.")
            self.is_connected = False

    def close(self):
        if self.driver:
            self.driver.close()

    def create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        node_id = properties.get("id") or properties.get("name") or str(len(self._memory_nodes) + 1)
        properties["id"] = str(node_id)
        label = label.strip()

        if self.is_connected and self.driver:
            try:
                with self.driver.session() as session:
                    # Sanitize Cypher label
                    query = f"MERGE (n:{label} {{id: $id}}) SET n += $props RETURN n"
                    result = session.run(query, id=str(node_id), props=properties)
                    record = result.single()
                    if record:
                        return dict(record["n"])
            except Exception as e:
                logger.warning(f"[NEO4J] Node creation failed on daemon ({e}). Falling back to memory graph.")
                self.is_connected = False

        # In-memory graph fallback
        node_key = f"{label}:{node_id}"
        self._memory_nodes[node_key] = {
            "id": str(node_id),
            "label": label,
            "properties": properties
        }
        return properties

    def create_relationship(
        self,
        from_label: str,
        from_id: str,
        rel_type: str,
        to_label: str,
        to_id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        properties = properties or {}
        rel_type = rel_type.strip().upper()

        if self.is_connected and self.driver:
            try:
                with self.driver.session() as session:
                    query = (
                        f"MATCH (a:{from_label} {{id: $from_id}}), (b:{to_label} {{id: $to_id}}) "
                        f"MERGE (a)-[r:{rel_type}]->(b) SET r += $props RETURN r"
                    )
                    session.run(query, from_id=str(from_id), to_id=str(to_id), props=properties)
                    return True
            except Exception as e:
                logger.warning(f"[NEO4J] Relationship creation failed on daemon ({e}). Falling back to memory graph.")
                self.is_connected = False

        # In-memory graph fallback
        self._memory_edges.append({
            "from_label": from_label,
            "from_id": str(from_id),
            "rel_type": rel_type,
            "to_label": to_label,
            "to_id": str(to_id),
            "properties": properties
        })
        return True

    def find_related_assets(self, asset_id: str) -> List[Dict[str, Any]]:
        if self.is_connected and self.driver:
            try:
                with self.driver.session() as session:
                    query = (
                        "MATCH (a {id: $asset_id})-[r]-(b) "
                        "RETURN labels(b) as labels, b as node, type(r) as relationship"
                    )
                    results = session.run(query, asset_id=str(asset_id))
                    output = []
                    for rec in results:
                        node_dict = dict(rec["node"])
                        output.append({
                            "labels": rec["labels"],
                            "node": node_dict,
                            "relationship": rec["relationship"]
                        })
                    return output
            except Exception as e:
                logger.warning(f"[NEO4J] Query failed on daemon ({e}). Falling back to memory graph.")

        # In-memory search fallback
        output = []
        for edge in self._memory_edges:
            if edge["from_id"] == str(asset_id):
                to_key = f"{edge['to_label']}:{edge['to_id']}"
                target_node = self._memory_nodes.get(to_key, {}).get("properties", {"id": edge["to_id"]})
                output.append({
                    "labels": [edge["to_label"]],
                    "node": target_node,
                    "relationship": edge["rel_type"]
                })
            elif edge["to_id"] == str(asset_id):
                from_key = f"{edge['from_label']}:{edge['from_id']}"
                source_node = self._memory_nodes.get(from_key, {}).get("properties", {"id": edge["from_id"]})
                output.append({
                    "labels": [edge["from_label"]],
                    "node": source_node,
                    "relationship": edge["rel_type"]
                })
        return output

    def find_asset_paths(self, asset_id_1: str, asset_id_2: str) -> List[Dict[str, Any]]:
        if self.is_connected and self.driver:
            try:
                with self.driver.session() as session:
                    query = (
                        "MATCH p = shortestPath((a {id: $id1})-[*..4]-(b {id: $id2})) "
                        "RETURN [n in nodes(p) | {id: n.id, name: n.name}] as path_nodes, "
                        "[r in relationships(p) | type(r)] as rels"
                    )
                    res = session.run(query, id1=str(asset_id_1), id2=str(asset_id_2))
                    record = res.single()
                    if record:
                        return {
                            "nodes": record["path_nodes"],
                            "relationships": record["rels"]
                        }
            except Exception as e:
                pass

        # Fallback BFS path search in memory graph
        return self._memory_bfs_path(asset_id_1, asset_id_2)

    def _memory_bfs_path(self, start_id: str, end_id: str) -> Dict[str, Any]:
        visited = set([str(start_id)])
        queue = [([str(start_id)], [])]
        while queue:
            node_path, rel_path = queue.pop(0)
            curr = node_path[-1]
            if curr == str(end_id):
                return {"nodes": [{"id": n} for n in node_path], "relationships": rel_path}

            for edge in self._memory_edges:
                nxt = None
                rel = edge["rel_type"]
                if edge["from_id"] == curr:
                    nxt = edge["to_id"]
                elif edge["to_id"] == curr:
                    nxt = edge["from_id"]

                if nxt and nxt not in visited:
                    visited.add(nxt)
                    queue.append((node_path + [nxt], rel_path + [rel]))

        return {"nodes": [], "relationships": []}

    def find_cross_domain_connections(self) -> List[Dict[str, Any]]:
        if self.is_connected and self.driver:
            try:
                with self.driver.session() as session:
                    query = (
                        "MATCH (a:Asset)-[r1]->(m)-[r2]->(b) "
                        "WHERE a.asset_type <> b.asset_type "
                        "RETURN a, type(r1) as rel1, m, type(r2) as rel2, b LIMIT 20"
                    )
                    res = session.run(query)
                    connections = []
                    for rec in res:
                        connections.append({
                            "asset_a": dict(rec["a"]),
                            "rel1": rec["rel1"],
                            "middle": dict(rec["m"]),
                            "rel2": rec["rel2"],
                            "asset_b": dict(rec["b"])
                        })
                    return connections
            except Exception as e:
                pass

        # Memory graph cross-domain scan
        connections = []
        for edge1 in self._memory_edges:
            for edge2 in self._memory_edges:
                if edge1["to_id"] == edge2["from_id"] and edge1["from_id"] != edge2["to_id"]:
                    n1_key = f"{edge1['from_label']}:{edge1['from_id']}"
                    n2_key = f"{edge2['to_label']}:{edge2['to_id']}"
                    n1 = self._memory_nodes.get(n1_key, {}).get("properties", {"id": edge1["from_id"]})
                    n2 = self._memory_nodes.get(n2_key, {}).get("properties", {"id": edge2["to_id"]})
                    connections.append({
                        "asset_a": n1,
                        "rel1": edge1["rel_type"],
                        "middle": {"id": edge1["to_id"]},
                        "rel2": edge2["rel_type"],
                        "asset_b": n2
                    })
                    if len(connections) >= 20:
                        break
        return connections

    def get_opportunity_context(self) -> Dict[str, Any]:
        # Aggregate graph stats & nodes
        nodes_summary = []
        relationships_summary = []

        if self.is_connected and self.driver:
            try:
                with self.driver.session() as session:
                    res = session.run("MATCH (n) RETURN labels(n)[0] as label, n.id as id, n.name as name, n.asset_type as type LIMIT 50")
                    for rec in res:
                        nodes_summary.append({
                            "label": rec["label"],
                            "id": rec["id"],
                            "name": rec["name"],
                            "type": rec["type"]
                        })
                    res_rel = session.run("MATCH (a)-[r]->(b) RETURN a.name as source, type(r) as rel, b.name as target LIMIT 50")
                    for rec in res_rel:
                        relationships_summary.append({
                            "source": rec["source"] or a.get("id"),
                            "relationship": rec["rel"],
                            "target": rec["target"] or b.get("id")
                        })
                    return {
                        "nodes": nodes_summary,
                        "relationships": relationships_summary
                    }
            except Exception as e:
                pass

        # In-memory graph summary
        for key, val in self._memory_nodes.items():
            props = val.get("properties", {})
            nodes_summary.append({
                "label": val.get("label"),
                "id": props.get("id"),
                "name": props.get("name"),
                "type": props.get("asset_type")
            })

        for edge in self._memory_edges:
            relationships_summary.append({
                "source": edge["from_id"],
                "relationship": edge["rel_type"],
                "target": edge["to_id"]
            })

        return {
            "nodes": nodes_summary,
            "relationships": relationships_summary
        }

    def get_full_graph() -> Dict[str, Any]:
        nodes = []
        edges = []

        if self.is_connected and self.driver:
            try:
                with self.driver.session() as session:
                    res_n = session.run("MATCH (n) RETURN id(n) as internal_id, labels(n) as labels, properties(n) as props")
                    for r in res_n:
                        nodes.append({
                            "id": str(r["props"].get("id", r["internal_id"])),
                            "labels": r["labels"],
                            "properties": r["props"]
                        })
                    res_e = session.run("MATCH (a)-[r]->(b) RETURN a.id as from_id, type(r) as type, b.id as to_id, properties(r) as props")
                    for r in res_e:
                        edges.append({
                            "from": str(r["from_id"]),
                            "to": str(r["to_id"]),
                            "type": r["type"],
                            "properties": r["props"]
                        })
                    return {"nodes": nodes, "edges": edges}
            except Exception:
                pass

        # In-memory graph
        for key, val in self._memory_nodes.items():
            props = val.get("properties", {})
            nodes.append({
                "id": props.get("id", key),
                "labels": [val.get("label")],
                "properties": props
            })
        for edge in self._memory_edges:
            edges.append({
                "from": edge["from_id"],
                "to": edge["to_id"],
                "type": edge["rel_type"],
                "properties": edge.get("properties", {})
            })
        return {"nodes": nodes, "edges": edges}


neo4j_service = Neo4jService()
