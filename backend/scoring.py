def normalize_score(score_val) -> float:
    """
    Normalizes a score value to a 0-100 range.
    Handles numeric strings, floats, and scales 0-10 up to 0-100.
    """
    if score_val is None:
        return 0.0
    try:
        val = float(score_val)
        if 0.0 <= val <= 10.0:
            return val * 10.0
        return max(0.0, min(100.0, val))
    except (ValueError, TypeError):
        return 0.0

def calculate_single_score(opp: dict) -> dict:
    """
    Calculates the overall score and detailed explanation for a single opportunity.
    Weights:
      - Market Potential: 30%
      - Feasibility: 25%
      - Strategic Fit: 20%
      - Asset Reusability: 15%
      - Confidence: 10%
    """
    m_score = normalize_score(opp.get("market_potential", 0.0))
    f_score = normalize_score(opp.get("feasibility", 0.0))
    s_score = normalize_score(opp.get("strategic_fit", 0.0))
    a_score = normalize_score(opp.get("asset_reusability", 0.0))
    c_score = normalize_score(opp.get("confidence", 0.0))

    overall = (
        (m_score * 0.30) +
        (s_score * 0.25) +
        (f_score * 0.20) +
        (a_score * 0.15) +
        (c_score * 0.10)
    )
    overall = round(overall, 1)  # Rounded to 1 decimal place as requested

    explanation = (
        f"Overall Score: {overall:.1f}/100. Breakdown:\n"
        f"- Market Potential (30%): {m_score:.1f}/100 (Contrib: {m_score * 0.30:.1f})\n"
        f"- Strategic Fit (25%): {s_score:.1f}/100 (Contrib: {s_score * 0.25:.1f})\n"
        f"- Feasibility (20%): {f_score:.1f}/100 (Contrib: {f_score * 0.20:.1f})\n"
        f"- Asset Reusability (15%): {a_score:.1f}/100 (Contrib: {a_score * 0.15:.1f})\n"
        f"- Confidence (10%): {c_score:.1f}/100 (Contrib: {c_score * 0.10:.1f})"
    )

    opp["market_potential"] = m_score
    opp["feasibility"] = f_score
    opp["strategic_fit"] = s_score
    opp["asset_reusability"] = a_score
    opp["confidence"] = c_score
    opp["overall_score"] = overall
    opp["score_explanation"] = explanation
    
    return opp

def score_and_rank_opportunities(opportunities: list) -> list:
    """
    Iterates through a list of opportunities, calculates scores for each, 
    and returns the list sorted in descending order of overall score.
    """
    if not opportunities:
        return []
        
    scored_list = []
    for opp in opportunities:
        scored_opp = calculate_single_score(opp)
        scored_list.append(scored_opp)
        
    scored_list.sort(key=lambda x: x["overall_score"], reverse=True)
    return scored_list
