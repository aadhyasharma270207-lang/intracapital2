from app.services.neo4j_service import neo4j_service


def test_neo4j_nodes_and_relationships():
    c_node = neo4j_service.create_node("Company", {"id": "c-100", "name": "Acme Industrial"})
    a_node = neo4j_service.create_node("Sensor_data", {"id": "a-200", "name": "Thermal Telemetry"})

    assert c_node["id"] == "c-100"
    assert a_node["id"] == "a-200"

    rel_created = neo4j_service.create_relationship(
        from_label="Company", from_id="c-100",
        rel_type="OWNS",
        to_label="Sensor_data", to_id="a-200"
    )
    assert rel_created is True

    related = neo4j_service.find_related_assets("c-100")
    assert len(related) >= 1
