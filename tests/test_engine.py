"""
Unit & Integration tests for ApexRev Multi-Agent Engine and SQLite Database.
"""

import os
from apexrev.engine import MultiAgentEngine
from apexrev.state import MissionStatus

def test_mission_flow_and_hitl():
    engine = MultiAgentEngine()
    
    # 1. Create a mission for custom target
    state = engine.create_mission(target_account="Snowflake Cloud", scenario_type="custom_intelligence")
    assert state.status == MissionStatus.PENDING
    assert state.current_node == "supervisor"
    
    # 2. Step through DAG nodes
    executed_state = engine.execute_step(state.mission_id)
    assert executed_state.status == MissionStatus.SUSPENDED_HITL
    assert executed_state.current_node == "hitl_gate"
    assert len(executed_state.research_signals) > 0
    assert len(executed_state.verified_citations) > 0
    assert executed_state.draft_artifact is not None
    assert executed_state.compliance_score > 0.50
    
    # 3. Test SQLite persistence
    retrieved = engine.db.get_mission(state.mission_id)
    assert retrieved is not None
    assert retrieved["mission_id"] == state.mission_id
    assert len(retrieved["logs"]) > 0

    # 4. Approve mission
    approved = engine.approve_mission(state.mission_id)
    assert approved.status == MissionStatus.COMPLETED
    assert "delivery" in approved.node_history
    print("\n[SUCCESS] test_mission_flow_and_hitl passed seamlessly with SQLite persistence!")

def test_dynamic_knowledge_ingestion():
    engine = MultiAgentEngine()
    test_doc_id = "DOC-TEST-99"
    engine.knowledge.add_document(
        doc_id=test_doc_id,
        title="Custom SOC3 Security Protocol",
        category="security",
        content="Zero-Trust end-to-end enclave with automated STIG security checks.",
        citations="Security Audit 2026"
    )
    
    # Search for this document
    results = engine.knowledge.hybrid_search("enclave STIG security checks", top_k=2)
    assert len(results) > 0
    matched_ids = [r["doc_id"] for r in results]
    assert test_doc_id in matched_ids
    print("\n[SUCCESS] test_dynamic_knowledge_ingestion passed seamlessly!")

if __name__ == "__main__":
    test_dynamic_knowledge_ingestion()
    test_mission_flow_and_hitl()
