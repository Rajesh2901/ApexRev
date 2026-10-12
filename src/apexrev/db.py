"""
Persistent SQLite database storage for ApexRev Platform.
Maintains missions, execution logs, grounded citations, and audit ledgers.
"""

import sqlite3
import json
import time
import os
from typing import Dict, Any, List, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "apexrev.db")

class Database:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._init_schema()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Missions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                mission_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                target_account TEXT NOT NULL,
                scenario_type TEXT NOT NULL,
                current_node TEXT NOT NULL,
                status TEXT NOT NULL,
                compliance_score REAL DEFAULT 0.0,
                draft_artifact TEXT,
                hitl_edited_content TEXT,
                requires_hitl INTEGER DEFAULT 1,
                total_tokens INTEGER DEFAULT 0,
                estimated_cost_usd REAL DEFAULT 0.0,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """)

            # Logs table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_id TEXT NOT NULL,
                node TEXT NOT NULL,
                agent TEXT NOT NULL,
                message TEXT NOT NULL,
                log_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
            )
            """)

            # Knowledge documents table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                citations TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """)

            # Audit ledger table (cryptographic tamper-evident record)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                signature TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """)

            conn.commit()

    def save_mission(self, state: Dict[str, Any]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO missions (
                mission_id, tenant_id, target_account, scenario_type,
                current_node, status, compliance_score, draft_artifact,
                hitl_edited_content, requires_hitl, total_tokens,
                estimated_cost_usd, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(mission_id) DO UPDATE SET
                current_node=excluded.current_node,
                status=excluded.status,
                compliance_score=excluded.compliance_score,
                draft_artifact=excluded.draft_artifact,
                hitl_edited_content=excluded.hitl_edited_content,
                requires_hitl=excluded.requires_hitl,
                total_tokens=excluded.total_tokens,
                estimated_cost_usd=excluded.estimated_cost_usd,
                updated_at=excluded.updated_at
            """, (
                state["mission_id"],
                state.get("tenant_id", "default"),
                state.get("target_account", ""),
                state.get("scenario_type", "custom"),
                state.get("current_node", "supervisor"),
                state.get("status", "pending"),
                state.get("compliance_score", 0.0),
                state.get("draft_artifact", ""),
                state.get("hitl_edited_content", ""),
                1 if state.get("requires_hitl", True) else 0,
                state.get("total_tokens", 0),
                state.get("estimated_cost_usd", 0.0),
                state.get("created_at", time.time()),
                time.time()
            ))
            conn.commit()

    def save_log(self, mission_id: str, node: str, agent: str, message: str, log_type: str = "info"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO logs (mission_id, node, agent, message, log_type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (mission_id, node, agent, message, log_type, time.time()))
            conn.commit()

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM missions WHERE mission_id = ?", (mission_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            mission = dict(row)
            
            # Fetch logs
            cursor.execute("SELECT * FROM logs WHERE mission_id = ? ORDER BY timestamp ASC", (mission_id,))
            mission["logs"] = [dict(log) for log in cursor.fetchall()]
            return mission

    def list_missions(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM missions ORDER BY updated_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def save_document(self, doc_id: str, title: str, category: str, content: str, citations: str, tenant_id: str = "default"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO documents (doc_id, tenant_id, title, category, content, citations, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(doc_id) DO UPDATE SET
                title=excluded.title,
                category=excluded.category,
                content=excluded.content,
                citations=excluded.citations
            """, (doc_id, tenant_id, title, category, content, citations, time.time()))
            conn.commit()

    def list_documents(self, tenant_id: str = "default") -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
