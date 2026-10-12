"""
State schemas and data models for the ApexRev Agent State Machine.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
import time
import uuid

class NodeStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SUSPENDED = "suspended"

class MissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUSPENDED_HITL = "suspended_hitl"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

@dataclass
class Signal:
    source: str
    category: str
    summary: str
    confidence: float
    raw_snippet: str

@dataclass
class Citation:
    doc_id: str
    title: str
    section: str
    similarity_score: float
    verified: bool

@dataclass
class AgentLog:
    timestamp: float
    node: str
    agent: str
    message: str
    log_type: str = "info"  # info, tool_call, observation, decision, error

@dataclass
class AgentState:
    mission_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = "tenant_enterprise_demo"
    target_account: str = ""
    scenario_type: str = "outbound_intelligence"  # outbound_intelligence, rfp_fulfillment, contract_audit
    
    current_node: str = "supervisor"
    status: MissionStatus = MissionStatus.PENDING
    
    # State accumulated across nodes
    research_signals: List[Dict[str, Any]] = field(default_factory=list)
    verified_citations: List[Dict[str, Any]] = field(default_factory=list)
    draft_artifact: Optional[str] = None
    compliance_score: float = 0.0
    
    # Human-in-the-Loop review state
    requires_hitl: bool = True
    hitl_approved_at: Optional[float] = None
    hitl_edited_content: Optional[str] = None
    
    # Telemetry and Execution Logs
    logs: List[Dict[str, Any]] = field(default_factory=list)
    node_history: List[str] = field(default_factory=list)
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def add_log(self, node: str, agent: str, message: str, log_type: str = "info"):
        self.logs.append({
            "timestamp": time.time(),
            "node": node,
            "agent": agent,
            "message": message,
            "type": log_type
        })
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
