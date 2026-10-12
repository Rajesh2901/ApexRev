"""
HTTP API and Static Web Server for ApexRev Platform.
Provides REST and Server-Sent Event streaming endpoints for agent monitoring and HITL actions.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse
import os
import sys
from typing import Dict, Any

from .engine import MultiAgentEngine
from .state import MissionStatus

engine = MultiAgentEngine()

class ApexRevHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve static files from static directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.static_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "static"))
        super().__init__(*args, directory=self.static_dir, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/missions/"):
            mission_id = path.replace("/api/missions/", "").strip("/")
            state = engine.get_mission(mission_id)
            if state:
                self._send_json(200, state.to_dict())
            else:
                self._send_json(404, {"error": "Mission not found"})
            return

        elif path == "/api/knowledge":
            docs = [
                {
                    "doc_id": d["doc_id"],
                    "title": d["title"],
                    "category": d["category"],
                    "citations": d["citations"]
                }
                for d in engine.knowledge.documents
            ]
            self._send_json(200, {"documents": docs, "total": len(docs)})
            return

        elif path == "/api/health":
            self._send_json(200, {"status": "healthy", "service": "ApexRev Agent Core", "version": "1.0.0"})
            return

        # Default static file serving (e.g. index.html)
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path == "/api/missions/create":
            target = body.get("target_account", "Databricks")
            scenario = body.get("scenario_type", "outbound_intelligence")
            state = engine.create_mission(target_account=target, scenario_type=scenario)
            self._send_json(201, state.to_dict())
            return

        elif path.endswith("/step"):
            parts = path.split("/")
            mission_id = parts[3]
            try:
                state = engine.execute_step(mission_id)
                self._send_json(200, state.to_dict())
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        elif path.endswith("/approve"):
            parts = path.split("/")
            mission_id = parts[3]
            edited_content = body.get("edited_content")
            try:
                state = engine.approve_mission(mission_id, edited_content=edited_content)
                self._send_json(200, state.to_dict())
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        elif path.endswith("/reject"):
            parts = path.split("/")
            mission_id = parts[3]
            reason = body.get("reason", "Operator rejected")
            try:
                state = engine.reject_mission(mission_id, reason=reason)
                self._send_json(200, state.to_dict())
            except Exception as e:
                self._send_json(400, {"error": str(e)})
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def _read_json_body(self) -> Dict[str, Any]:
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len > 0:
            raw = self.rfile.read(content_len).decode("utf-8")
            try:
                return json.loads(raw)
            except Exception:
                return {}
        return {}

    def _send_json(self, status: int, data: Dict[str, Any]):
        response = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response)

def start_server(host: str = "127.0.0.1", port: int = 8000):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    server = HTTPServer((host, port), ApexRevHandler)
    print("\n=======================================================")
    print(f"[*] ApexRev Agent Platform Running at: http://{host}:{port}")
    print("=======================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down ApexRev server...")
        server.server_close()

