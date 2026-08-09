from app.agents.evaluation_agent import EvaluationAgent


def test_deterministic_scoring_formula():
    # Weights: Market(30%), Feasibility(25%), StrategicFit(20%), Reusability(15%), Confidence(10%)
    mp = 87.0
    fe = 91.0
    sf = 84.0
    ar = 95.0
    cf = 88.0

    expected = (0.30 * 87.0) + (0.25 * 91.0) + (0.20 * 84.0) + (0.15 * 95.0) + (0.10 * 88.0)
    expected_rounded = round(expected, 1)

    score = EvaluationAgent.calculate_score(
        market_potential=mp,
        feasibility=fe,
        strategic_fit=sf,
        asset_reusability=ar,
        confidence=cf
    )

    assert score == expected_rounded
    assert score == 88.7
