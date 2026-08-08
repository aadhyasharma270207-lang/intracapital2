import unittest
from unittest.mock import patch, MagicMock
from backend.services.granite_service import GraniteService, get_watsonx_credentials

class TestGraniteService(unittest.TestCase):
    @patch("backend.services.granite_service.get_watsonx_credentials")
    def test_missing_credentials(self, mock_creds):
        """
        Tests initialization behavior when credentials are blank.
        """
        mock_creds.return_value = {
            "api_key": "",
            "project_id": "",
            "url": "https://us-south.ml.cloud.ibm.com",
            "model_id": "ibm/granite-13b-instruct-v2"
        }
        
        service = GraniteService()
        self.assertFalse(service.is_configured)
        self.assertEqual(service.mode_label, "💡 DEMO MODE" if "LIVE" in service.mode_label else "🟡 DEMO MODE")
        
        # Calling generate should raise ValueError
        with self.assertRaises(ValueError):
            service.generate("hello")

    @patch("backend.services.granite_service.ModelInference")
    @patch("backend.services.granite_service.get_watsonx_credentials")
    def test_api_timeout_handling(self, mock_creds, mock_inference):
        """
        Tests API error handling and timeouts wrapping.
        """
        mock_creds.return_value = {
            "api_key": "somekey",
            "project_id": "someproj",
            "url": "https://us-south.ml.cloud.ibm.com",
            "model_id": "ibm/granite-13b-instruct-v2"
        }
        
        # Setup mock ModelInference to raise timeout error
        mock_instance = MagicMock()
        mock_instance.generate_text.side_effect = Exception("Read timeout on Watsonx servers")
        mock_inference.return_value = mock_instance
        
        service = GraniteService()
        self.assertTrue(service.is_configured)
        
        with self.assertRaises(RuntimeError) as context:
            service.generate("hello")
            
        self.assertIn("timed out", str(context.exception))

    def test_json_extraction_clean(self):
        """
        Tests extraction of JSON bodies from markdown wrappers.
        """
        service = GraniteService()
        raw_llm = """
Here is the JSON:
```json
{
  "opportunities": [{"name": "Platform"}]
}
```
Footnote.
"""
        extracted = service._extract_json(raw_llm)
        self.assertIsNotNone(extracted)
        self.assertIn("opportunities", extracted)
        self.assertEqual(extracted["opportunities"][0]["name"], "Platform")

    @patch.object(GraniteService, "generate")
    def test_controlled_json_repair_retry(self, mock_generate):
        """
        Tests that JSON parser executes a second call if the first output is malformed.
        """
        # First call yields bad json; second call yields corrected JSON
        mock_generate.side_effect = [
            "bad json that cannot be parsed {",
            '{"opportunities": [{"name": "Repaired Opportunity"}]}'
        ]
        
        service = GraniteService()
        # Force credentials configuration to allow run
        service.is_configured = True
        
        res = service.generate_json("discover")
        self.assertEqual(mock_generate.call_count, 2)
        self.assertEqual(res["opportunities"][0]["name"], "Repaired Opportunity")

if __name__ == "__main__":
    unittest.main()
