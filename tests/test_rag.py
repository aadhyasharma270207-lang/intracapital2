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
from backend.services import rag_service
from backend import config

class TestRagService(unittest.TestCase):
    def setUp(self):
        # Redirect vectorstore directory to a temporary path for isolated testing
        self.orig_store = config.VECTORSTORE_DIR
        self.test_dir = Path(tempfile.mkdtemp())
        config.VECTORSTORE_DIR = self.test_dir
        
    def tearDown(self):
        # Reset configuration
        config.VECTORSTORE_DIR = self.orig_store
        rag_service.clear_index()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_indexing_and_semantic_retrieval(self):
        """
        Tests indexing document chunks and retrieving them semantically.
        """
        if not rag_service.CHROMADB_AVAILABLE:
            self.skipTest("ChromaDB is not installed in the system.")
            
        rag_service.initialize()
        
        test_chunks = [
            {
                "text": "The low-power sensor beacon US-10492811-B2 monitors microclimates inside cargo containers.",
                "source": "patents.txt",
                "filename": "patents.txt",
                "file_type": "txt",
                "page": 1,
                "chunk_id": "c1"
            },
            {
                "text": "Rotary industrial compressors exhibit bearing wear leading to mechanical breakdown.",
                "source": "operations.txt",
                "filename": "operations.txt",
                "file_type": "txt",
                "page": 2,
                "chunk_id": "c2"
            }
        ]
        
        # Build index
        rag_service.index_documents(test_chunks)
        
        # Test semantic search query
        results = rag_service.retrieve_evidence("microclimate sensor beacons", n_results=1)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["filename"], "patents.txt")
        self.assertIn("US-10492811-B2", results[0]["text"])
        self.assertTrue(results[0]["relevance"] > 0)
        self.assertEqual(results[0]["page"], 1)
        
        # Test clear index
        rag_service.clear_index()
        results_post = rag_service.retrieve_evidence("sensor beacons", n_results=1)
        self.assertEqual(len(results_post), 0)
        
if __name__ == "__main__":
    unittest.main()
