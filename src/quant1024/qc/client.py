"""
QuantConnect REST API Client
"""

import time
import json
import hashlib
import base64
from typing import Dict, Any, Optional

try:
    import requests
except ImportError:
    print("Please install requests first: pip install requests")
    exit(1)

from .models import QCCredentials


BASE_URL = "https://www.quantconnect.com/api/v2"


class QuantConnectAPI:
    """QuantConnect REST API client"""

    def __init__(self, credentials: QCCredentials):
        self.credentials = credentials
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """Generate authentication headers"""
        timestamp = str(int(time.time()))

        # Calculate hash: sha256(token:timestamp)
        timestamped_token = f"{self.credentials.api_token}:{timestamp}"
        hashed_token = hashlib.sha256(timestamped_token.encode("utf-8")).hexdigest()

        # Base64 encode: userId:hashedToken
        auth_string = f"{self.credentials.user_id}:{hashed_token}"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

        return {
            "Authorization": f"Basic {auth_base64}",
            "Timestamp": timestamp,
            "Content-Type": "application/json",
        }

    def _post(self, path: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Send POST request"""
        url = f"{BASE_URL}{path}"
        headers = self._get_headers()

        response = self.session.post(url, headers=headers, json=data or {})

        try:
            result = response.json()
        except json.JSONDecodeError:
            raise Exception(f"Non-JSON response: {response.text}")

        if not response.ok:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        if result.get("success") is False:
            errors = result.get("errors") or result.get("messages") or result
            raise Exception(f"QC API error: {errors}")

        return result

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Send GET request"""
        url = f"{BASE_URL}{path}"
        headers = self._get_headers()

        response = self.session.get(url, headers=headers, params=params)

        try:
            result = response.json()
        except json.JSONDecodeError:
            raise Exception(f"Non-JSON response: {response.text}")

        return result

    def authenticate(self) -> bool:
        """Verify authentication"""
        print("🔐 Verifying authentication...")
        result = self._post("/authenticate", {})
        print("   ✓ Authentication successful")
        return True

    def create_project(self, name: str, language: str = "Py") -> int:
        """Create project"""
        print(f"📁 Creating project: {name}...")
        result = self._post("/projects/create", {
            "name": name,
            "language": language,
        })
        
        # Parse projectId
        project_id = None
        if "projects" in result and result["projects"]:
            project_id = result["projects"][0].get("projectId")
        elif "projectId" in result:
            project_id = result["projectId"]

        if not project_id:
            raise Exception(f"Unable to get projectId: {result}")
        
        print(f"   ✓ Project created successfully, ID: {project_id}")
        return project_id

    def create_file(self, project_id: int, name: str, content: str) -> bool:
        """Create or update file"""
        print(f"📄 Uploading file: {name}...")
        
        try:
            # Try to create first
            self._post("/files/create", {
                "projectId": project_id,
                "name": name,
                "content": content,
            })
        except Exception as e:
            if "already exist" in str(e).lower() or "exists" in str(e).lower():
                # If already exists, update
                print("   File already exists, updating...")
                self._post("/files/update", {
                    "projectId": project_id,
                    "name": name,
                    "content": content,
                })
            else:
                raise e
        
        print("   ✓ File uploaded successfully")
        return True

    def compile(self, project_id: int) -> str:
        """Compile project"""
        print("🔨 Compiling project...")
        result = self._post("/compile/create", {"projectId": project_id})
        
        compile_id = result.get("compileId")
        if not compile_id:
            raise Exception(f"Unable to get compileId: {result}")
        
        print(f"   Compile ID: {compile_id}")
        return compile_id

    def wait_for_compile(
        self, project_id: int, compile_id: str, timeout: int = 120
    ) -> bool:
        """Wait for compilation to complete"""
        print("   Waiting for compilation to complete...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self._post(
                "/compile/read",
                {
                    "projectId": project_id,
                    "compileId": compile_id,
                },
            )

            state = result.get("state")

            if state == "BuildSuccess":
                print("   ✓ Compilation successful")
                return True
            elif state == "BuildError":
                errors = result.get("errors") or result.get("logs") or result
                raise Exception(f"Compilation error: {errors}")
            
            print(f"   Status: {state}...")
            time.sleep(2)
        
        raise Exception(f"Compilation timeout ({timeout} seconds)")

    def create_backtest(self, project_id: int, compile_id: str, name: str) -> str:
        """Create backtest"""
        print(f"🚀 Creating backtest: {name}...")
        result = self._post("/backtests/create", {
            "projectId": project_id,
            "compileId": compile_id,
            "backtestName": name,
        })
        
        backtest_id = None
        if "backtest" in result:
            backtest_id = result["backtest"].get("backtestId")
        elif "backtestId" in result:
            backtest_id = result["backtestId"]
        
        if not backtest_id:
            raise Exception(f"Unable to get backtestId: {result}")
        
        print(f"   Backtest ID: {backtest_id}")
        return backtest_id

    def wait_for_backtest(
        self, project_id: int, backtest_id: str, timeout: int = 600
    ) -> Dict:
        """Wait for backtest to complete"""
        print("   Waiting for backtest to complete...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self._post("/backtests/read", {
                "projectId": project_id,
                "backtestId": backtest_id,
            })
            
            backtest = result.get("backtest", {})
            completed = backtest.get("completed")
            progress = backtest.get("progress", 0)
            status = backtest.get("status", "")
            
            if completed is True:
                print("   ✓ Backtest complete!")
                return backtest
            
            if "error" in str(status).lower():
                raise Exception(f"Backtest error: {backtest}")
            
            progress_pct = progress * 100 if isinstance(progress, float) else progress
            print(f"   Progress: {progress_pct:.1f}%")
            time.sleep(3)
        
        raise Exception(f"Backtest timeout ({timeout} seconds)")

    def get_backtest_orders(
        self, project_id: int, backtest_id: str, max_orders: int = 100
    ) -> list:
        """Get order records (paginated)"""
        print("📋 Getting order records...")
        
        all_orders = []
        start = 0
        batch_size = 100  # API limits to max 100 orders per request

        while start < max_orders:
            end = min(start + batch_size, max_orders)

            result = self._post(
                "/backtests/orders/read",
                {
                    "projectId": project_id,
                    "backtestId": backtest_id,
                    "start": start,
                    "end": end,
                },
            )

            orders = result.get("orders", [])
            if not orders:
                break

            all_orders.extend(orders)

            if len(orders) < batch_size:
                break

            start = end

        print(f"   ✓ Retrieved {len(all_orders)} orders")
        return all_orders

    def get_full_backtest_with_charts(self, project_id: int, backtest_id: str) -> Dict:
        """Get complete backtest results with chart data"""
        print("📈 Getting complete backtest data (including charts)...")
        
        result = self._get("/backtests/read", {
            "projectId": project_id,
            "backtestId": backtest_id,
        })
        
        backtest = result.get("backtest", {})
        charts = backtest.get("charts", {})
        
        print(f"   ✓ Retrieved {len(charts)} charts")
        return backtest
