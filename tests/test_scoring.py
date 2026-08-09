import unittest
from backend import scoring

class TestScoring(unittest.TestCase):
    def test_normalize_score(self):
        """
        Tests that score normalization maps 0-10 up to 0-100.
        """
        self.assertEqual(scoring.normalize_score(8.5), 85.0)
        self.assertEqual(scoring.normalize_score(92.0), 92.0)
        self.assertEqual(scoring.normalize_score(None), 0.0)
        self.assertEqual(scoring.normalize_score("invalid"), 0.0)

    def test_overall_weighted_score(self):
        """
        Tests the 30% / 25% / 20% / 15% / 10% weights formula.
        Verify it rounds to 1 decimal place.
        """
        opp = {
            "name": "Opportunity Test",
            "market_potential": 90, # 27.0 contribution
            "feasibility": 80,        # 16.0 contribution
            "strategic_fit": 70,     # 17.5 contribution
            "asset_reusability": 85, # 12.75 contribution
            "confidence": 95,        # 9.5 contribution
            # Total expected = 82.75 -> rounded to 82.8
        }
        
        scored = scoring.calculate_single_score(opp)
        self.assertEqual(scored["overall_score"], 82.8)
        self.assertIn("score_explanation", scored)
        self.assertIn("Contrib: 27.0", scored["score_explanation"])

    def test_ranking_sort(self):
        """
        Tests that opportunities list is sorted in descending order of overall score.
        """
        opps = [
            {"name": "Low Match", "market_potential": 40, "feasibility": 40, "strategic_fit": 40, "asset_reusability": 40, "confidence": 40},
            {"name": "High Match", "market_potential": 90, "feasibility": 90, "strategic_fit": 90, "asset_reusability": 90, "confidence": 90}
        ]
        
        ranked = scoring.score_and_rank_opportunities(opps)
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0]["name"], "High Match")
        self.assertEqual(ranked[1]["name"], "Low Match")
        self.assertTrue(ranked[0]["overall_score"] > ranked[1]["overall_score"])

if __name__ == "__main__":
    unittest.main()
