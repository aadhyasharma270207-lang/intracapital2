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
import pandas as pd
from backend.services import ingestion_service

class TestIngestionService(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_clean_text(self):
        """
        Tests text normalization.
        """
        raw = "  Hello   world!  \n\n\nNew   line.  "
        expected = "Hello world!\n\nNew line."
        self.assertEqual(ingestion_service.clean_text(raw), expected)

    def test_chunk_text(self):
        """
        Tests text chunk overlaps and keys.
        """
        text = "abcdefghijklmnopqrstuvwxyz"
        chunks = ingestion_service.chunk_text(text, filename="test.txt", file_type="txt", chunk_size=10, chunk_overlap=2)
        self.assertTrue(len(chunks) >= 2)
        self.assertEqual(chunks[0]["text"], "abcdefghij")
        self.assertEqual(chunks[0]["filename"], "test.txt")
        self.assertEqual(chunks[0]["file_type"], "txt")
        self.assertIn("chunk_id", chunks[0])

    def test_telemetry_csv_excursions(self):
        """
        Tests CSV telemetry anomaly logic.
        """
        csv_file = self.test_dir / "test_sensors.csv"
        data = [
            ["2026-07-10T12:00:00Z", "WH-101", 3.0, 60.0, "N/A"],
            ["2026-07-10T13:00:00Z", "WH-101", 12.5, 80.0, "N/A"],
            ["2026-07-10T14:00:00Z", "C-801", -18.0, 40.0, "SH-1112"],
            ["2026-07-10T15:00:00Z", "C-801", 1.5, 70.0, "SH-1112"]
        ]
        df = pd.DataFrame(data, columns=["timestamp", "warehouse_id", "temperature", "humidity", "shipment_id"])
        df.to_csv(csv_file, index=False)
        
        chunks = ingestion_service.process_csv(csv_file)
        self.assertTrue(len(chunks) > 0)
        
        text_content = chunks[0]["text"]
        self.assertIn("EXCURSION in WH-101", text_content)
        self.assertIn("EXCURSION in C-801", text_content)

    def test_corrupt_files_safety(self):
        """
        Ensures that bad/missing extensions do not crash the pipeline.
        """
        bad_file = self.test_dir / "corrupt.pdf"
        with open(bad_file, "w") as f:
            f.write("not a real pdf content")
            
        chunks = ingestion_service.ingest_file(bad_file)
        self.assertTrue(len(chunks) > 0)
        self.assertIn("Error loading file", chunks[0]["text"])
        self.assertEqual(chunks[0]["file_type"], "pdf")

if __name__ == "__main__":
    unittest.main()
