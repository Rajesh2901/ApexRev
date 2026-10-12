"""
HTTP API and Static Web Server for ApexRev Platform.
Provides REST endpoints for mission lifecycle, dynamic knowledge ingestion, history, and exports.
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.static_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "static"))
        super().__init__(*args, directory=self.static_dir, **kwargs)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With, Accept")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/missions":
            missions = engine.list_missions(limit=25)
            self._send_json(200, {"missions": missions, "total": len(missions)})
            return

        elif path.startswith("/api/missions/") and path.endswith("/export"):
            mission_id = path.replace("/api/missions/", "").replace("/export", "").strip("/")
            mission = engine.get_mission(mission_id)
            if not mission:
                self._send_json(404, {"error": "Mission not found"})
                return

            content = mission.get("hitl_edited_content") or mission.get("draft_artifact") or "No content available."
            export_text = (
                f"# ApexRev Mission Deliverable: {mission.get('target_account', 'N/A')}\n"
                f"Status: {mission.get('status', 'unknown')}\n"
                f"Compliance Score: {mission.get('compliance_score', 0) * 100:.1f}%\n"
                f"Generated At: {mission.get('created_at')}\n"
                f"---------------------------------------------------\n\n"
                f"{content}\n"
            ).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="mission_{mission_id[:8]}.md"')
            self.send_header("Content-Length", str(len(export_text)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(export_text)
            return

        elif path.startswith("/api/missions/"):
            mission_id = path.replace("/api/missions/", "").strip("/")
            state = engine.get_mission(mission_id)
            if state:
                self._send_json(200, state)
            else:
                self._send_json(404, {"error": "Mission not found"})
            return

        elif path == "/api/knowledge":
            docs = engine.knowledge.db.list_documents()
            self._send_json(200, {"documents": docs, "total": len(docs)})
            return

        elif path == "/api/health":
            self._send_json(200, {
                "status": "healthy",
                "service": "ApexRev Agent Core",
                "version": "2.5.0",
                "live_llm_active": engine.llm.has_live_llm(),
                "persistence": "SQLite (apexrev.db)"
            })
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path == "/api/missions/create":
            target = body.get("target_account", "Enterprise Target")
            scenario = body.get("scenario_type", "custom")
            custom_instructions = body.get("custom_instructions", "")
            state = engine.create_mission(
                target_account=target,
                scenario_type=scenario,
                custom_instructions=custom_instructions
            )
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

        elif path == "/api/knowledge/add":
            title = body.get("title", "Untitled Document")
            category = body.get("category", "general")
            content = body.get("content", "")
            citations = body.get("citations", "Manual Upload")
            doc_id = f"DOC-USER-{int(os.times().system * 1000)}"

            engine.knowledge.add_document(doc_id, title, category, content, citations)
            self._send_json(201, {"status": "created", "doc_id": doc_id, "title": title})
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
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With, Accept")
        self.send_header("Access-Control-Allow-Private-Network", "true")
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
    print(f"[*] Persistent SQLite Storage: apexrev.db")
    print(f"[*] Live API & UI Ready")
    print("=======================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down ApexRev server...")
        server.server_close()
