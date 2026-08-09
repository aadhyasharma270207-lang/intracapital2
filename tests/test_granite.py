from app.services.granite_service import granite_service


def test_granite_service_fallback():
    prompt = "Evaluate this business opportunity"
    result = granite_service.generate_json(prompt)
    assert isinstance(result, dict)
    assert "market_potential" in result
    assert "feasibility" in result
