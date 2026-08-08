import unittest
import tempfile
import os
from pathlib import Path

# Redirect temp folder for process space isolation on Windows
if Path("D:/temp").exists() or os.path.exists("D:\\temp"):
    tempfile.tempdir = "D:\\temp"
else:
    Path("scratch/temp").mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(Path("scratch/temp").resolve())

import shutil
from unittest.mock import patch
from backend import config
from backend import pipeline

class TestPipeline(unittest.TestCase):
    def setUp(self):
        # Setup temporary directories for isolation
        self.orig_store = config.VECTORSTORE_DIR
        self.test_dir = Path(tempfile.mkdtemp())
        self.uploads_dir = self.test_dir / "uploads"
        self.vector_dir = self.test_dir / "vectorstore"
        
        self.uploads_dir.mkdir()
        self.vector_dir.mkdir()
        
        config.UPLOADS_DIR = self.uploads_dir
        config.VECTORSTORE_DIR = self.vector_dir

    def tearDown(self):
        # Restore configuration
        config.VECTORSTORE_DIR = self.orig_store
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch("backend.services.granite_service.get_watsonx_credentials")
    def test_pipeline_demo_mode_execution(self, mock_creds):
        """
        Tests the end-to-end integration runner in Demo Mode.
        """
        # Ensure credentials resolve to blank (Demo Mode active)
        mock_creds.return_value = {
            "api_key": "",
            "project_id": "",
            "url": "https://us-south.ml.cloud.ibm.com",
            "model_id": "ibm/granite-13b-instruct-v2"
        }
        
        # Write dummy files to uploads
        txt_path = self.uploads_dir / "patents.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Company Patent: PAT-US-10492811-B2 wireless mesh beacons telemetry monitors.")
            
        csv_path = self.uploads_dir / "sensor_data.csv"
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("timestamp,warehouse_id,temperature,humidity,shipment_id\n2026-07-10T12:00:00Z,WH-101,3.2,55.0,N/A\n")
            
        # Execute pipeline
        report = pipeline.run_pipeline(str(self.uploads_dir))
        
        # Assertions
        self.assertEqual(report["status"], "DEMO_MODE")
        self.assertEqual(len(report["opportunities"]), 3)
        self.assertIn("Cold Chain Intelligence Platform", report["opportunities"][0]["name"])
        self.assertTrue(report["chunks_created"] > 0)
        self.assertEqual(len(report["errors"]), 0)
        
        # Ensure scores exist and are ranked
        opp = report["opportunities"][0]
        self.assertIn("overall_score", opp)
        self.assertIn("score_explanation", opp)

if __name__ == "__main__":
    unittest.main()
