"""
Unit tests for ApexRev Multi-Agent Engine and State Machine.
"""

from apexrev.engine import MultiAgentEngine
from apexrev.state import MissionStatus

def test_mission_flow_and_hitl():
    engine = MultiAgentEngine()
    
    # 1. Create a mission
    state = engine.create_mission(target_account="Databricks", scenario_type="outbound_intelligence")
    assert state.status == MissionStatus.PENDING
    assert state.current_node == "supervisor"
    
    # 2. Execute steps up to HITL interruption
    executed_state = engine.execute_step(state.mission_id)
    assert executed_state.status == MissionStatus.SUSPENDED_HITL
    assert executed_state.current_node == "hitl_gate"
    assert len(executed_state.research_signals) > 0
    assert len(executed_state.verified_citations) > 0
    assert executed_state.draft_artifact is not None
    assert executed_state.compliance_score >= 0.90
    
    # 3. Approve mission via HITL
    approved_state = engine.approve_mission(state.mission_id)
    assert approved_state.status == MissionStatus.COMPLETED
    assert "delivery" in approved_state.node_history
    print("\n[SUCCESS] test_mission_flow_and_hitl passed seamlessly!")

def test_knowledge_hybrid_search():
    engine = MultiAgentEngine()
    results = engine.knowledge.hybrid_search("Delta Lake multi-region metadata failover", top_k=2)
    assert len(results) > 0
    assert results[0]["similarity_score"] > 0.60
    print("\n[SUCCESS] test_knowledge_hybrid_search passed seamlessly!")

if __name__ == "__main__":
    test_knowledge_hybrid_search()
    test_mission_flow_and_hitl()
