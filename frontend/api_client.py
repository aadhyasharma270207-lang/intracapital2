import os
import httpx
from typing import Optional, Dict, Any, List

class APIClient:
    """
    Centralized HTTP client wrapper for INTRACAPITAL backend API.
    Handles X-API-Key authentication, timeout bounds, and translates connection issues into friendly user messages.
    """
    def __init__(self):
        # Allow backend address to be set via environment variable
        self.backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
        
        # Read authentication key
        self.api_key = os.getenv("FASTAPI_INTERNAL_API_KEY", "")
        
    @property
    def headers(self) -> Dict[str, str]:
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _request(self, method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None, files_data: Optional[List[Any]] = None, timeout: float = 120.0) -> Dict[str, Any]:
        url = f"{self.backend_url}{endpoint}"
        try:
            with httpx.Client(timeout=timeout) as client:
                if method.upper() == "GET":
                    response = client.get(url, headers=self.headers)
                elif method.upper() == "POST":
                    if files_data:
                        response = client.post(url, headers=self.headers, files=files_data)
                    else:
                        response = client.post(url, headers=self.headers, json=json_data)
                else:
                    return {"status": "error", "error": f"Unsupported method: {method}"}
                
                # Check authentication key denial explicitly
                if response.status_code in [401, 403]:
                    return {
                        "status": "error",
                        "error": "Access Denied: Invalid X-API-Key token. Please verify your FASTAPI_INTERNAL_API_KEY environment variable."
                    }
                
                response.raise_for_status()
                return response.json()
                
        except httpx.ConnectError:
            return {
                "status": "error",
                "error": f"Backend Connection Refused. Ensure the FastAPI server is running at {self.backend_url}."
            }
        except httpx.TimeoutException:
            return {
                "status": "error",
                "error": f"Request to {endpoint} timed out after {timeout} seconds."
            }
        except httpx.HTTPStatusError as e:
            try:
                detail = e.response.json().get("detail", str(e))
            except Exception:
                detail = e.response.text or str(e)
            return {"status": "error", "error": f"Backend Error ({response.status_code}): {detail}"}
        except Exception as e:
            return {"status": "error", "error": f"Unexpected Connection Error: {str(e)}"}

    def check_health(self) -> Dict[str, Any]:
        """GET /health"""
        return self._request("GET", "/health", timeout=15.0)

    def get_metrics(self) -> Dict[str, Any]:
        """GET /metrics"""
        return self._request("GET", "/metrics", timeout=10.0)

    def upload_files(self, files: List[Any]) -> Dict[str, Any]:
        """POST /upload"""
        return self._request("POST", "/upload", files_data=files, timeout=60.0)

    def run_analyze(self) -> Dict[str, Any]:
        """POST /analyze"""
        return self._request("POST", "/analyze", timeout=120.0)

    def run_discover(self) -> Dict[str, Any]:
        """POST /discover"""
        return self._request("POST", "/discover", timeout=120.0)

    def get_opportunities(self) -> Dict[str, Any]:
        """GET /opportunities"""
        return self._request("GET", "/opportunities", timeout=15.0)

    def get_opportunity_details(self, opp_id: str) -> Dict[str, Any]:
        """GET /opportunity/{opp_id}"""
        return self._request("GET", f"/opportunity/{opp_id}", timeout=15.0)

    def validate_opportunity(self, req_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /validate-opportunity"""
        return self._request("POST", "/validate-opportunity", json_data=req_data, timeout=15.0)

    def expand_business_model(self, req_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /expand-business-model"""
        return self._request("POST", "/expand-business-model", json_data=req_data, timeout=60.0)

    def reset_pipeline(self) -> Dict[str, Any]:
        """POST /reset"""
        return self._request("POST", "/reset", timeout=20.0)

    def load_demo_data(self) -> Dict[str, Any]:
        """POST /load-demo-data"""
        return self._request("POST", "/load-demo-data", timeout=20.0)

    def get_architecture(self) -> Dict[str, Any]:
        """GET /architecture"""
        return self._request("GET", "/architecture", timeout=10.0)

    def get_root(self) -> Dict[str, Any]:
        """GET /"""
        return self._request("GET", "/", timeout=5.0)
