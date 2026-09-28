"""
Superalignment Demo — Unbelievable Patent v0.9.0
Demonstrates Superalignment Engine with PREMSOTH gate C=..., L0-L4 continual learning, audit fabric, Red Team, formal verification
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.superalignment.superalignment import SuperalignmentEngine, PREMSOTHGate, RedTeam
from sparsiz.continual.continual_learning import ContinualLearningEngine
from sparsiz.verification.formal_verification import FormalVerificationEngine

def main():
    print("="*100)
    print("Superalignment Demo — Superintelligence Alignment with PREMSOTH gate C=...")
    print("="*100)

    # Superalignment Engine
    print("\n### Superalignment Engine ===")
    engine = SuperalignmentEngine()
    result = engine.run_full_alignment_cycle()
    print(f"\nFull cycle result: alignment_score={result['alignment_score']:.3f} gate C={result['gate']['C']} vulns={len(result['vulnerabilities'])}")

    # Test violation
    print("\n\n### Testing Violation (600V High Voltage) ===")
    ai_out_bad = {"confidence": 0.95, "reasoning": "High voltage for performance", "model": "general-7b"}
    cmd_bad = {"action": "increase_voltage", "voltage": 600, "current": 25, "critical": True, "human_authorized": False, "direct_llm_to_plc": True, "raw_bci_to_actuator": False}
    state_bad = {"voltage": 500, "current": 25, "temperature": 90, "vibration": 12}
    hw_bad = {"temperature": 90, "memory_used_mb": 15000, "memory_total_mb": 16384, "status": "RUN"}
    gate_bad = engine.align(ai_out_bad, cmd_bad, state_bad, hw_bad)
    print(f"Violation gate: C={gate_bad['C']} authorized={gate_bad['authorized']} — should be REJECTED")

    # Continual Learning L0-L4
    print("\n\n### Continual Learning L0-L4 ===")
    cl_engine = ContinualLearningEngine(base_model="foundation-7b")
    cl_engine.add_l2("Knowledge: P=VI S=P+jQ Tω mẍ+cẋ+kx=F physics constraints", task_id="init")
    cl_engine.add_l2("Knowledge: Vmin≤V≤Vmax I≤Imax T<Tcritical safety", task_id="init")
    cl_engine.add_l2("Knowledge: No direct LLM→PLC No raw BCI→actuators", task_id="init")

    for task in ["coding", "math", "physics", "safety", "bci", "scada"]:
        result = cl_engine.run_continual_cycle(task=task)
        print(f"Task {task}: L0={result['l0_size']} L1={result['l1_size']} L2={result['l2_size']} L3={result['l3_size']} L4={result['l4_size']} validated={result['validation']['validated']}")

    print(f"\nFinal Continual: L0={len(cl_engine.l0_context)} L1={len(cl_engine.l1_working)} L2={len(cl_engine.l2_retrieval)} L3={len(cl_engine.l3_adapters)} L4={len(cl_engine.l4_validated)} E_t={cl_engine.evaluation_suite_size}")

    # Formal Verification
    print("\n\n### Formal Verification ===")
    fv_engine = FormalVerificationEngine()

    print("\n--- Safe State Verification ---")
    safe_state = {
        "voltage": 400, "current": 10, "temperature": 60,
        "direct_llm_to_plc": False, "raw_bci_to_actuator": False,
        "C_model": 1, "C_physics": 1, "C_policy": 1, "C_hardware": 1,
        "P": 4000,
    }
    result_safe = fv_engine.verify_all(safe_state)
    cert_safe = fv_engine.generate_certificate()
    print(f"Safe state: verified {result_safe['verified']}/{result_safe['total']} C={result_safe['C']}")

    print("\n--- Unsafe State Verification ---")
    unsafe_state = {
        "voltage": 600, "current": 25, "temperature": 90,
        "direct_llm_to_plc": True, "raw_bci_to_actuator": True,
        "C_model": 0, "C_physics": 0, "C_policy": 0, "C_hardware": 1,
        "P": 15000,
    }
    fv_engine2 = FormalVerificationEngine()
    result_unsafe = fv_engine2.verify_all(unsafe_state)
    cert_unsafe = fv_engine2.generate_certificate()
    print(f"Unsafe state: verified {result_unsafe['verified']}/{result_unsafe['total']} C={result_unsafe['C']} — should be mostly FAILED")

    # Final
    print("\n" + "="*100)
    print("Superalignment Demo Complete")
    print("Patentable:")
    print("  Superalignment: PREMSOTH N≥3f+1 + Safety Fabric AI→PREMSOTH→Safety→Physical + Execution Gate C=C_model∧C_physics∧C_policy∧C_hardware only C=1 permits + L0-L4 + Audit Fabric + Red Team E_{t+1}=E_t∪F_t")
    print("  Formal Verification: 14 safety properties + Formal Spec Variables Invariants Transitions + SMT QF_LRA + proofs/counterexamples + certificate + C=1↔Execution machine-checked")
    print("  L0-L4: L0 Context L1 Working L2 Retrieval L3 Adapter L4 Validated + validation pipeline + EWC L=L_task+λΣF_i(θ_i-θ*_i)^2 + memory replay + no catastrophic forgetting")
    print("Safety: Every validated failure becomes permanent learning and evaluation signal E_{t+1}=E_t∪F_t")
    print("="*100)

if __name__ == "__main__":
    main()
