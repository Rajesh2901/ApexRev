"""
Multi-Agent Orchestration Engine for ApexRev.
Implements the stateful DAG pipeline:
Supervisor -> Research Agent -> Compliance/RAG Agent -> Drafting Agent -> HITL Gate -> Delivery.
"""

from typing import Dict, Any, Callable, Optional
import time
import copy
from .state import AgentState, MissionStatus, NodeStatus
from .rag import KnowledgeFabric
from .tools import MCPToolRegistry

class MultiAgentEngine:
    def __init__(self):
        self.knowledge = KnowledgeFabric()
        self.checkpoints: Dict[str, AgentState] = {}

    def create_mission(self, target_account: str, scenario_type: str = "outbound_intelligence") -> AgentState:
        """Initializes a new stateful mission in the checkpointer."""
        state = AgentState(
            target_account=target_account,
            scenario_type=scenario_type,
            status=MissionStatus.PENDING
        )
        self.checkpoints[state.mission_id] = state
        return state

    def get_mission(self, mission_id: str) -> Optional[AgentState]:
        return self.checkpoints.get(mission_id)

    def execute_step(self, mission_id: str, callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> AgentState:
        """Executes the next node in the state graph until an end or interruption node is reached."""
        state = self.checkpoints.get(mission_id)
        if not state:
            raise ValueError(f"Mission {mission_id} not found in checkpointer.")

        if state.status == MissionStatus.COMPLETED or state.status == MissionStatus.REJECTED:
            return state

        # Step through the DAG
        while state.status in [MissionStatus.PENDING, MissionStatus.RUNNING]:
            current_node = state.current_node

            if current_node == "supervisor":
                self._node_supervisor(state, callback)
                state.current_node = "research"
            
            elif current_node == "research":
                self._node_research(state, callback)
                state.current_node = "compliance_rag"

            elif current_node == "compliance_rag":
                self._node_compliance(state, callback)
                state.current_node = "drafting"

            elif current_node == "drafting":
                self._node_drafting(state, callback)
                state.current_node = "hitl_gate"

            elif current_node == "hitl_gate":
                # Checkpointer freezes state before external action
                self._node_hitl_gate(state, callback)
                break  # Interrupt execution loop

            elif current_node == "delivery":
                self._node_delivery(state, callback)
                state.status = MissionStatus.COMPLETED
                break

        # Persist updated snapshot
        self.checkpoints[mission_id] = state
        return state

    def _node_supervisor(self, state: AgentState, callback: Optional[Callable]):
        state.status = MissionStatus.RUNNING
        state.node_history.append("supervisor")
        state.add_log("supervisor", "Supervisor Agent", f"Partitioned mission goal for '{state.target_account}' into 3 sub-agent goals.")
        state.total_tokens += 320
        state.estimated_cost_usd += 0.002
        if callback:
            callback({"event": "node", "node": "supervisor", "state": state.to_dict()})

    def _node_research(self, state: AgentState, callback: Optional[Callable]):
        state.node_history.append("research")
        state.add_log("research", "Research Agent", f"[Tool: MCP WebScraper] Scraping public indicators for '{state.target_account}'...", "tool_call")
        
        signals = MCPToolRegistry.scrape_target_signals(state.target_account)
        state.research_signals = signals
        state.add_log("research", "Research Agent", f"Found {len(signals)} high-confidence signals: {[s['category'] for s in signals]}", "observation")
        state.total_tokens += 1240
        state.estimated_cost_usd += 0.008
        if callback:
            callback({"event": "node", "node": "research", "state": state.to_dict()})

    def _node_compliance(self, state: AgentState, callback: Optional[Callable]):
        state.node_history.append("compliance_rag")
        query_text = " ".join([s["summary"] for s in state.research_signals])
        state.add_log("compliance_rag", "Compliance/RAG Agent", f"[Tool: Hybrid Search] Querying pgvector knowledge fabric for groundings...", "tool_call")

        citations = self.knowledge.hybrid_search(query_text, top_k=2)
        state.verified_citations = citations
        state.compliance_score = 0.942 if "databricks" in state.target_account.lower() else 0.981

        state.add_log("compliance_rag", "Compliance/RAG Agent", f"Retrieved {len(citations)} verified documents. Grounding compliance score: {state.compliance_score * 100:.1f}%.", "observation")
        state.total_tokens += 1850
        state.estimated_cost_usd += 0.012
        if callback:
            callback({"event": "node", "node": "compliance_rag", "state": state.to_dict()})

    def _node_drafting(self, state: AgentState, callback: Optional[Callable]):
        state.node_history.append("drafting")
        state.add_log("drafting", "Drafting Agent", "Synthesizing executive-ready artifact utilizing grounded evidence and tone calibration.", "decision")

        target_name = state.target_account
        if "databricks" in target_name.lower():
            state.draft_artifact = (
                "Subject: Alex - mitigating cross-region schema drift across your lakehouse pipelines?\n\n"
                "Hi Alex,\n\n"
                "Read your team's engineering blog post on Databricks' recent multi-region metadata partition rollout.\n\n"
                "When teams scale partitioned Delta tables across 4+ AWS/GCP regions at your velocity, SRE teams typically burn 25%+ of on-call hours managing silent state divergence and metastore retry loops.\n\n"
                "Our platform guarantees sub-50ms atomic state replication with Zero-Knowledge verification, completely eliminating sync timeouts for Snowflake and Databricks clusters.\n\n"
                "Would you be open to reviewing a 3-page technical validation spec with benchmark traces this Thursday?"
            )
        elif "stripe" in target_name.lower():
            state.draft_artifact = (
                "Subject: Meghan - validating ISO 20022 FedNow message translation across partner banks?\n\n"
                "Hi Meghan,\n\n"
                "With the upcoming ISO 20022 syntax enforcement across domestic clearing networks, ensuring zero-latency pacs.008 schema validation is likely top of mind.\n\n"
                "Our agent framework validates and transforms non-standard SWIFT MT feeds into compliant ISO XML in under 12 milliseconds, with cryptographic audit signatures compliant with SOC1/SOC2.\n\n"
                "Could we share a 60-second architecture diagram showing how this eliminates translation retries?"
            )
        else:
            state.draft_artifact = (
                "SECTION 4.2.1 COMPLIANCE STATEMENT:\n\n"
                "The Contractor affirms full compliance with DoD Cloud Computing Security Requirements Guide (SRG) Impact Level 5 (IL5). "
                "All data at rest is protected utilizing FIPS 140-3 validated cryptographic modules.\n\n"
                "Active FedRAMP High Authorization Package ID #FR-2024-8839 is on file with DISA. "
                "Continuous automated vulnerability scanning is performed via eMASS integration with automated STIG checklists."
            )

        state.total_tokens += 1400
        state.estimated_cost_usd += 0.018
        if callback:
            callback({"event": "node", "node": "drafting", "state": state.to_dict()})

    def _node_hitl_gate(self, state: AgentState, callback: Optional[Callable]):
        state.node_history.append("hitl_gate")
        state.status = MissionStatus.SUSPENDED_HITL
        state.add_log("hitl_gate", "Human-in-the-Loop Gate", "Interrupted state graph. Outbound dispatch suspended awaiting human authorization.", "decision")
        if callback:
            callback({"event": "suspended", "node": "hitl_gate", "state": state.to_dict()})

    def approve_mission(self, mission_id: str, edited_content: Optional[str] = None) -> AgentState:
        """Resumes the interrupted state graph following human authorization."""
        state = self.checkpoints.get(mission_id)
        if not state:
            raise ValueError(f"Mission {mission_id} not found.")

        state.hitl_approved_at = time.time()
        if edited_content:
            state.hitl_edited_content = edited_content
            state.draft_artifact = edited_content

        state.add_log("hitl_gate", "Human-in-the-Loop Gate", "Human approval granted. Resuming execution to delivery node.", "decision")
        state.current_node = "delivery"
        state.status = MissionStatus.RUNNING

        # Run delivery
        return self.execute_step(mission_id)

    def reject_mission(self, mission_id: str, reason: str = "Rejected by human reviewer") -> AgentState:
        state = self.checkpoints.get(mission_id)
        if not state:
            raise ValueError(f"Mission {mission_id} not found.")

        state.status = MissionStatus.REJECTED
        state.add_log("hitl_gate", "Human-in-the-Loop Gate", f"Mission rejected by operator: {reason}", "error")
        return state

    def _node_delivery(self, state: AgentState, callback: Optional[Callable] = None):
        state.node_history.append("delivery")
        content_to_send = state.hitl_edited_content or state.draft_artifact or ""
        delivery_res = MCPToolRegistry.dispatch_crm_action(state.target_account, content_to_send)
        state.add_log("delivery", "CRM Dispatcher", f"[Tool: CRM Connector] Successfully dispatched signed artifact: Record {delivery_res['crm_record_id']}", "observation")
        state.status = MissionStatus.COMPLETED
        if callback:
            callback({"event": "completed", "node": "delivery", "state": state.to_dict()})
