def test_opportunity_discovery_api(client):
    res = client.post("/api/v1/opportunities/discover", json={"company_name": "Test Company"})
    assert res.status_code == 200
    data = res.json()
    assert "analysis_id" in data
    assert data["opportunities_discovered"] >= 1
    opps = data["opportunities"]
    assert len(opps) >= 1

    first_opp = opps[0]
    assert "opportunity_id" in first_opp
    assert "score" in first_opp
    assert first_opp["score"] > 0

    # Test GET opportunity detail
    detail_res = client.get(f"/api/v1/opportunities/{first_opp['opportunity_id']}")
    assert detail_res.status_code == 200

    # Test POST opportunity explain
    explain_res = client.post(f"/api/v1/opportunities/{first_opp['opportunity_id']}/explain")
    assert explain_res.status_code == 200
    explain_data = explain_res.json()
    assert "explanation" in explain_data
    assert "score_breakdown" in explain_data
