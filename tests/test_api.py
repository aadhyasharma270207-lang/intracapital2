import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

# Redirect temp folder for process space isolation on Windows
if Path("D:/temp").exists() or os.path.exists("D:\\temp"):
    tempfile.tempdir = "D:\\temp"
else:
    Path("scratch/temp").mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(Path("scratch/temp").resolve())

from backend.api import app
from backend import config

class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Backup configuration keys
        self.orig_key = config.FASTAPI_INTERNAL_API_KEY
        
    def tearDown(self):
        config.FASTAPI_INTERNAL_API_KEY = self.orig_key

    def test_root_and_health(self):
        """
        Tests the / and /health endpoints.
        """
        res_root = self.client.get("/")
        self.assertEqual(res_root.status_code, 200)
        self.assertEqual(res_root.json()["application"], "INTRACAPITAL")
        
        res_health = self.client.get("/health")
        self.assertEqual(res_health.status_code, 200)
        health_data = res_health.json()
        self.assertIn("fastapi", health_data)
        self.assertIn("rag", health_data)
        self.assertIn("chromadb", health_data)
        self.assertIn("granite", health_data)

    def test_auth_unauthorized_denial(self):
        """
        Tests that endpoints verify the internal API key when configured.
        """
        # Configure internal secret key
        config.FASTAPI_INTERNAL_API_KEY = "hackathonsecret123"
        
        # Call protected endpoint without headers
        res = self.client.post("/reset")
        self.assertEqual(res.status_code, 401)
        self.assertIn("Authorization", res.json()["detail"])
        
        # Call protected endpoint with bad header
        headers = {"Authorization": "Bearer badtoken"}
        res = self.client.post("/reset", headers=headers)
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid", res.json()["detail"])
        
        # Call with correct header
        headers = {"Authorization": "Bearer hackathonsecret123"}
        res = self.client.post("/reset", headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_validate_opportunity_endpoint(self):
        """
        Tests that validation slider recalculation returns appropriate math bounds.
        """
        # Load demo opportunities into manager
        headers = {}
        if config.FASTAPI_INTERNAL_API_KEY:
            headers["Authorization"] = f"Bearer {config.FASTAPI_INTERNAL_API_KEY}"
            
        self.client.get("/opportunities", headers=headers)
        
        payload = {
            "opportunity_id": "opp_cold_chain_1",
            "market_potential": 100.0,
            "feasibility": 100.0,
            "strategic_fit": 100.0,
            "asset_reusability": 100.0,
            "confidence": 100.0
        }
        
        res = self.client.post("/validate-opportunity", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        
        val_data = res.json()
        self.assertEqual(val_data["opportunity_id"], "opp_cold_chain_1")
        self.assertEqual(val_data["adjusted_score"], 100.0)
        self.assertTrue(val_data["difference"] > 0)
        self.assertIn("Adjusted Overall Score", val_data["score_explanation"])

if __name__ == "__main__":
    unittest.main()
