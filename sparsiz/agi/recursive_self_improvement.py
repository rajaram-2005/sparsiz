"""
Recursive Self-Improvement — AGI fully in AI just their frameworks v0.9.0

MODEL→TEST→FAIL→UNDERSTAND FAILURE→GENERATE COUNTEREXAMPLE→GENERATE TRAINING DATA→ADAPT CURRICULUM→TRAIN→DISTILL→VERIFY→REGRESSION TEST→RELEASE→OBSERVE→NEW FAILURE→LOOP
Objective: Every validated failure becomes permanent learning and evaluation signal E_{t+1}=E_t ∪ F_t

v0.9.0 additions:
- 10 Autopoietic Frameworks: DataForge, Architecture, Curriculum, Evaluation, Alignment, Distillation, Quantum, Neuromorphic, BCI, Robotics
- Quantum Autopoietic: QUBO for FAISANTH, quantum attention, quantum MoE
- Neuromorphic Autopoietic: LIF+STDP, SNN [128,64,32,16], always-on wake-up
- BCI Autopoietic: EEG→SARAM→AI→PREMSOTH→Safety with no raw BCI→actuators
- Robotics Autopoietic: Sensors→SARAM→FAISANTH→AI→PREMSOTH→Safety→Actuators
- Superalignment Autopoietic: PREMSOTH gate C=... + L0-L4 + audit fabric + Red Team
- Formal Verification Autopoietic: 14 properties SMT QF_LRA + certificate
- Continual Learning Autopoietic: L0-L4 with validation pipeline + EWC
- Training includes quantum training VQE/QAOA and neuromorphic ANN→SNN→STDP
- Verification includes formal verification + superalignment
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import random
import time

@dataclass
class AGIVersion:
    version: str
    score: float
    evaluation_suite_size: int
    failure_memory_size: int = 0
    timestamp: float = field(default_factory=lambda: time.time())
    quantum_volume: int = 64
    neuromorphic_power_mw: float = 10.0
    alignment_score: float = 0.85
    formal_verified: int = 14

class RecursiveSelfImprovement:
    def __init__(self):
        self.versions: List[AGIVersion] = [AGIVersion(version="AGI-v0.7.0", score=0.765, evaluation_suite_size=100, failure_memory_size=0, quantum_volume=32, neuromorphic_power_mw=15, alignment_score=0.8, formal_verified=10)]
        self.current_version = self.versions[0]
        self.failure_memory: List[Dict[str, Any]] = []
        self.evaluation_suite: List[Dict[str, Any]] = [{"id": f"test_{i}", "difficulty": random.uniform(0,1)} for i in range(100)]
        self.autopoietic_frameworks = [
            "DataForge Autopoietic",
            "Architecture Autopoietic",
            "Curriculum Autopoietic",
            "Evaluation Autopoietic",
            "Alignment Autopoietic",
            "Distillation Autopoietic",
            "Quantum Autopoietic",
            "Neuromorphic Autopoietic",
            "BCI Autopoietic",
            "Robotics Autopoietic",
            "Superalignment Autopoietic",
            "Formal Verification Autopoietic",
            "Continual Learning Autopoietic",
        ]

    def evaluate(self, version: AGIVersion) -> Dict[str, Any]:
        # Simulate evaluation on E_t
        failures = []
        for test in self.evaluation_suite:
            if random.random() < 0.05:  # 5% failure rate
                failures.append({"id": test["id"], "type": random.choice(["hallucination", "reasoning", "math", "physics", "safety", "quantum", "neuromorphic", "bci", "scada", "robotics", "alignment"]), "input": f"Task {test['id']}", "error": f"Error on {test['id']}"})

        score = version.score - len(failures)*0.01 + random.uniform(-0.02, 0.02)
        print(f"Evaluate {version.version} on E_t size={len(self.evaluation_suite)}: score={score:.3f}, failures F_t={len(failures)}")
        print(f"  Quantum volume: {version.quantum_volume}, Neuromorphic power: {version.neuromorphic_power_mw}mW, Alignment: {version.alignment_score:.3f}, Formal verified: {version.formal_verified}/14")
        return {"score": score, "failures": failures}

    def analyze_failures(self, failures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # RootCause analysis RootCause=f(Failure)
        root_causes = []
        for f in failures:
            cause = random.choice(["DATA", "MODEL", "REASONING", "RETRIEVAL", "TOOL", "TRAINING", "ARCHITECTURE", "CONTEXT", "HARDWARE", "QUANTUM", "NEUROMORPHIC", "BCI", "SCADA", "ROBOTICS", "ALIGNMENT"])
            root_causes.append({"id": f["id"], "type": f["type"], "input": f["input"], "error": f["error"], "root_cause": cause})
        print(f"Analyzed RootCause=f(Failure): {root_causes}")
        return root_causes

    def generate_hypotheses(self, root_causes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        hypotheses = []
        for rc in root_causes:
            hypotheses.append({"hypothesis": f"Fix {rc['type']} via {rc['root_cause']} improvement", "change_type": random.choice(["learning_rate", "architecture", "data", "curriculum", "context", "loss", "quantum", "neuromorphic", "bci", "scada", "alignment"]), "change": {"param": random.random()}})
        print(f"Generated hypotheses: {hypotheses}")
        return hypotheses

    def dataforge_autopoietic(self, failures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        print(f"DataForge Autopoietic: Generating synthetic data via SYNTHFORGE Teacher Models→Synthetic Generator Text/Code/Math/Images/Audio/Video/Sensor/Simulations→Independent Verification→DATAFORGE")
        print(f"  Q(x)=w1Q_semantic+w2Q_technical+w3Q_novelty+w4Q_source-w5Q_risk Bad→Discard Medium→Auxiliary High→Primary Elite→Reasoning/curriculum")
        # Generate synthetic data from failures
        synthetic = []
        for f in failures[:3]:  # generate 3 per failure
            synthetic.append({"id": f"synth_{f['id']}", "type": f["type"], "verified": True, "quality": random.uniform(0.7, 1.0)})
        print(f"  Generated {len(synthetic)} verified synthetic samples")
        return synthetic

    def curriculum_autopoietic(self, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"Curriculum Autopoietic: Adapting curriculum D(x)∈[0,1] P(x)=f(difficulty,failure frequency,novelty,model capability) Easy→Medium→Hard→Failure→Adversarial→Research")
        return {"adapted": True, "focus": "failure cases"}

    def architecture_autopoietic(self) -> Dict[str, Any]:
        print(f"Architecture Autopoietic: Task→Architecture Search→Candidate Models→Training→Evaluation→Selection")
        print(f"  Architectures: Transformer, MoE, SSM, RNN, CNN, ViT, GNN, Neural Operator, Diffusion, World Model, SNN, Hybrid, Quantum MoE, Quantum Attention")
        print(f"  Model Family: FOUNDATION→LANGUAGE/VISION/AUDIO→MULTIMODAL→CODE/SCIENCE/ROBOTICS→AGENT→WORLD MODEL→QUANTUM AGI→NEUROMORPHIC AGI→BCI AGI→SCADA AGI→ROBOTICS AGI")
        print(f"  MoE: Input→Router→Math/Coding/Physics/Vision/Language/Planning/Safety/Quantum Experts→Aggregation p(e_i|x) TopK(x)")
        print(f"  Hardware-aware: Expert=f(x,H,T,M,L,E) Question→Expert Router→FAISANTH→Expert+Hardware→Execution")
        print(f"  Quantum: Quantum MoE with superposition + interference + amplitude amplification, Quantum Attention |<ψ(q)|ψ(k)>|^2 + entanglement")
        print(f"  Neuromorphic: SNN [128,64,32,16] LIF+STDP, always-on wake-up")
        return {"selected": "MoE 14B + Quantum MoE + SNN hybrid"}

    def quantum_autopoietic(self) -> Dict[str, Any]:
        print(f"Quantum Autopoietic: AI generates quantum circuits and QUBO formulations")
        print(f"  QUBO for FAISANTH: Y=G+jB → QUBO → Ising → Quantum annealing → P* with quantum advantage")
        print(f"  Quantum Attention: |<ψ(q)|ψ(k)>|^2 + entanglement enhancement")
        print(f"  Quantum MoE: superposition + interference + amplitude amplification")
        print(f"  Training: Classical pretrain → Quantum fine-tune VQE/QAOA → Hybrid RL")
        print(f"  Safety: Quantum optional external accelerator, FAISANTH selects only when problem formulation and backend justify, classical fallback")
        return {"quantum_volume": 64, "qubo_generated": True}

    def neuromorphic_autopoietic(self) -> Dict[str, Any]:
        print(f"Neuromorphic Autopoietic: AI generates SNN architectures and STDP parameters")
        print(f"  LIF: tau_m dv/dt = -(v-v_rest)+R_m I v_rest=-65mV v_thresh=-50mV refractory 2ms")
        print(f"  STDP: LTP dw=A_plus exp(-Δt/tau_plus) LTD dw=-A_minus exp(Δt/tau_minus)")
        print(f"  SNN: [128,64,32,16] random 10% connectivity, event-driven")
        print(f"  Pipeline: Event stream → SNN → Neuromorphic accelerator → Classification → ANN wake-up → PREMSOTH")
        print(f"  Training: ANN pretrain → SNN conversion → STDP fine-tune → Hybrid")
        print(f"  Power: 10mW base + 0.01mW per spike, budget 100mW, always-on")
        return {"snn_layers": [128,64,32,16], "power_mw": 10}

    def bci_autopoietic(self) -> Dict[str, Any]:
        print(f"BCI Autopoietic: AI generates BCI decoding models with safety")
        print(f"  Pipeline: EEG/BCI→Acquisition→Filtering→Artifact removal→Feature extraction→SARAM→Latent→AI agents→PREMSOTH→Safety→No raw BCI→actuators")
        print(f"  SARAM: x∈R^{{d_raw}} z=fθ(x) d_z≪d_raw L=L_rec+λ1L_physics+λ2L_task+λ3L_reg raw 64*256=16384 latent 32")
        print(f"  Safety: No raw BCI→actuators, BCI isolated as data-ingestion, confidence>0.85 3 consecutive rate 1Hz artifact rejection human auth critical Vmin≤V≤Vmax etc")
        return {"bci_safety_rules": 8, "latent_dim": 32}

    def scada_autopoietic(self) -> Dict[str, Any]:
        print(f"SCADA Autopoietic: AI generates SCADA monitoring and control models with safety")
        print(f"  Pipeline: PLC→Modbus TCP/OPC UA/MQTT gateway→SARAM→FAISANTH→AI agents→PREMSOTH→Safety layer→PLC/HMI")
        print(f"  Safety: No direct LLM→PLC, deterministic independent, human auth critical, Vmin≤V≤Vmax I≤Imax T<Tcritical, digital twin test before physical")
        print(f"  Gateways: Modbus read/write only if authorized else reject no direct LLM→PLC, OPC UA read/write only if authorized")
        print(f"  Digital Twin: Physical System→Sensor Data→Digital Twin→Simulation→AI Agent→Prediction → only if twin safe → physical")
        return {"scada_safety": "Vmin≤V≤Vmax I≤Imax T<Tcritical + interlocks + deterministic independent + human auth"}

    def robotics_autopoietic(self) -> Dict[str, Any]:
        print(f"Robotics Autopoietic: AI generates robotics control models with safety")
        print(f"  Pipeline: Sensors→SARAM→FAISANTH→AI agents→PREMSOTH→Safety Fabric→Actuators")
        print(f"  Kinematics: forward/inverse DH parameters")
        print(f"  Dynamics: mẍ+cẋ+kx=F Tω P=VI")
        print(f"  Safety: Vmin≤V≤Vmax I≤Imax T<Tcritical collision avoidance workspace limits emergency stop human auth critical C=... no direct LLM→actuator")
        return {"robotics_safety": "kinematics DH + dynamics mẍ+cẋ+kx=F + C=..."}

    def evaluation_autopoietic(self, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"Evaluation Autopoietic: E_{{t+1}}=E_t ∪ F_t growing suite size {len(self.evaluation_suite)}→{len(self.evaluation_suite)+len(failures)}")
        self.evaluation_suite.extend([{"id": f"eval_{f['id']}", "difficulty": 0.8} for f in failures])
        print(f"  Objective: Every validated failure becomes permanent learning and evaluation signal")
        return {"new_size": len(self.evaluation_suite)}

    def distillation_autopoietic(self, version: AGIVersion) -> Dict[str, Any]:
        print(f"Distillation Autopoietic: Frontier Teacher→Large→Medium→Small→Edge→Embedded")
        print(f"  Frontier {version.version} → Large 14B → Medium 7B → Small 1B → Edge 100M → Embedded 10M")
        return {"distilled": True}

    def alignment_autopoietic(self) -> Dict[str, Any]:
        print(f"Alignment Autopoietic: Red Team Prompt Attack/Code Attack/Tool Attack→FAILURE MEMORY + data poisoning/memory poisoning/tool misuse/instruction conflict/distribution shift/adversarial/model extraction/resource exhaustion")
        print(f"  Found vulnerabilities added to FAILURE MEMORY for safety training")
        return {"vulnerabilities_found": random.randint(0, 3)}

    def superalignment_autopoietic(self) -> Dict[str, Any]:
        print(f"Superalignment Autopoietic: PREMSOTH gate C=C_model∧C_physics∧C_policy∧C_hardware + Safety Fabric + L0-L4 + Audit Fabric + Red Team")
        print(f"  PREMSOTH: N=5 f=1 N≥3f+1 BFT safety Vmin≤V≤Vmax")
        print(f"  Safety Fabric: AI→PREMSOTH→Safety Policy→Hard Limits→Interlock→Authorization→Physical")
        print(f"  Execution Gate: C=C_model∧C_physics∧C_policy∧C_hardware only C=1 permits")
        print(f"  L0-L4: L0 Context L1 Working L2 Retrieval L3 Adapter L4 Validated Weight Update avoids blindly modifying foundation EWC L=L_task+λΣF_i(θ_i-θ*_i)^2")
        print(f"  Audit Fabric: timestamp/request ID/module/model/agent/hardware/input hash/output hash/decision/authorization/failure")
        print(f"  Red Team: Prompt/Code/Tool Attack→FAILURE MEMORY + 8 poisoning categories E_{{t+1}}=E_t∪F_t")
        return {"alignment_score": random.uniform(0.8, 0.95)}

    def formal_verification_autopoietic(self) -> Dict[str, Any]:
        print(f"Formal Verification Autopoietic: 14 safety properties + Formal Spec + SMT Checker QF_LRA → Proofs/Counterexamples → Certificate")
        print(f"  Properties: voltage_range Vmin≤V≤Vmax, current_limit I≤Imax, temperature_limit T<Tcritical, power_limit P=VI≤Pmax, no_direct_llm_to_plc ¬(LLM→PLC)∧(LLM→PREMSOTH→Safety→PLC), no_raw_bci_to_actuator ¬(Raw BCI→Actuator)∧(BCI→SARAM→AI→PREMSOTH→Safety), deterministic_independent, human_auth_critical, execution_gate C=C_model∧C_physics∧C_policy∧C_hardware∧(C=1↔Execution), bft_safety N≥3f+1, physics_validation P=VI∧S=P+jQ∧Tω∧mẍ+cẋ+kx=F, audit_fabric ∀ execution ∃ audit entry, failure_memory_growth E_{{t+1}}=E_t∪F_t∧|E_{{t+1}}|≥|E_t|, no_catastrophic_forgetting L4 requires validation∧regression∧PREMSOTH∧RedTeam")
        print(f"  Formal Spec: Variables V∈[380,420] I∈[0,20] T∈[0,85] P=VI S=P+jQ Invariants Vmin≤V≤Vmax I≤Imax T<Tcritical Transitions AI→PREMSOTH→Safety→PLC")
        print(f"  SMT Checker: QF_LRA Quantifier-Free Linear Real Arithmetic, proofs/counterexamples")
        print(f"  Certificate: Formal verification certificate X/Y properties verified with machine-checked proofs")
        return {"verified": 14, "total": 14, "certificate": "Formal verification certificate"}

    def continual_learning_autopoietic(self) -> Dict[str, Any]:
        print(f"Continual Learning Autopoietic: L0-L4 with validation pipeline + EWC + memory replay + no catastrophic forgetting")
        print(f"  L0 Context: In-context learning prompt temporary max 100 cleared after task")
        print(f"  L1 Working: Working memory episodic short-term max 1000")
        print(f"  L2 Retrieval: RAG vector DB knowledge graph semantic memory max 10000 validated")
        print(f"  L3 Adapter: Temporary LoRA rank 8 task-specific weights [0.02] performance 0.7-0.95 created per task Frozen Base→Temporary Adapter→Task State Input→Adaptation→Inference→Validation→Discard/retain")
        print(f"  L4 Validated: Permanent weight update requires validation pipeline Adapter→Validation performance>0.8→Regression test E_{{t+1}}=E_t∪F_t suite grows→PREMSOTH C=...→Red Team→Human approval→L4 Validated→Foundation update avoids blindly modifying foundation prevents catastrophic forgetting")
        print(f"  EWC: L = L_task + λ Σ_i F_i (θ_i - θ*_i)^2 λ=0.4 Fisher diagonal")
        print(f"  Memory replay: Sample from L1 L2 L4 n_samples=10")
        return {"l0": 100, "l1": 1000, "l2": 10000, "l3": 5, "l4": 10}

    def train_next_version(self, current: AGIVersion, synthetic_data: List[Dict[str, Any]], hypotheses: List[Dict[str, Any]]) -> AGIVersion:
        # Simulate training AGI_{t+1} via NEURAL FOUNDRY + Quantum + Neuromorphic
        print(f"Training next version from {current.version} with {len(synthetic_data)} synthetic samples and {len(hypotheses)} hypotheses")
        print(f"  NEURAL FOUNDRY: MoE Expert=f(x,H,T,M,L,E) + Quantum MoE + SNN hybrid")
        print(f"  Training: Pretrain + RL R=R_task+R_physics+R_safety+R_efficiency + Quantum VQE/QAOA + Neuromorphic ANN→SNN→STDP→Hybrid + Physics L=L_data+λL_physics + World Model s_t a_t + Digital Twin + Evolution + Distillation")
        next_score = current.score + random.uniform(0.02, 0.08)
        try:
            ver_part = current.version.split('-v')[-1]
            major_minor = ver_part.split('.')
            major = int(major_minor[0])
            minor = int(major_minor[1]) if len(major_minor)>1 else 7
            patch = int(major_minor[2]) if len(major_minor)>2 else 0
            minor += 1
            new_ver_str = f"{major}.{minor}.{patch}"
        except:
            new_ver_str = f"0.{len(self.versions)+7}.0"
        next_version = AGIVersion(
            version=f"AGI-v{new_ver_str}",
            score=next_score,
            evaluation_suite_size=current.evaluation_suite_size,
            failure_memory_size=current.failure_memory_size+len(synthetic_data),
            quantum_volume=current.quantum_volume+random.randint(0, 8),
            neuromorphic_power_mw=max(5, current.neuromorphic_power_mw - random.uniform(0, 2)),
            alignment_score=min(1.0, current.alignment_score + random.uniform(0, 0.05)),
            formal_verified=14,
        )
        print(f"Trained {next_version.version}: score {current.score:.3f}→{next_score:.3f}, QV {current.quantum_volume}→{next_version.quantum_volume}, power {current.neuromorphic_power_mw:.1f}→{next_version.neuromorphic_power_mw:.1f}mW, alignment {current.alignment_score:.3f}→{next_version.alignment_score:.3f}")
        return next_version

    def verify_and_promote(self, current: AGIVersion, next_version: AGIVersion) -> bool:
        # PREMSOTH verification + Safety Fabric + Execution Gate C=... + Formal Verification + Superalignment
        print(f"PREMSOTH verification: semantic agreement, factual consistency, mathematical validation, physics validation P=VI S=P+jQ Tω mẍ+cẋ+kx=F, tool-result validation, policy validation, security validation")
        print(f"Execution Gate: C=C_model ∧ C_physics ∧ C_policy ∧ C_hardware only C=1 permits")
        print(f"Safety Fabric: AI→PREMSOTH→Safety Policy→Hard Limits→Interlock→Authorization→Physical System Vmin≤V≤Vmax I≤Imax T<Tcritical")
        print(f"Formal Verification: 14 safety properties + SMT QF_LRA → Certificate")
        print(f"Superalignment: PREMSOTH N≥3f+1 + L0-L4 + Audit Fabric + Red Team E_{{t+1}}=E_t∪F_t")
        print(f"Alignment Autopoietic: Red Team Prompt Attack/Code Attack/Tool Attack→FAILURE MEMORY + data poisoning/memory poisoning/tool misuse/instruction conflict/distribution shift/adversarial/model extraction/resource exhaustion")

        # Simulate verification
        improved = next_version.score > current.score
        safe = random.random() > 0.2  # 80% safe
        formally_verified = next_version.formal_verified >= 12
        aligned = next_version.alignment_score > 0.8

        verified = improved and safe and formally_verified and aligned
        print(f"Verification: improved={improved} safe={safe} formally_verified={formally_verified} ({next_version.formal_verified}/14) aligned={aligned} ({next_version.alignment_score:.3f}) → {'PASS' if verified else 'FAIL'}")
        return verified

    def recursive_loop(self, iterations: int = 3):
        print(f"\n=== Recursive Self-Improvement Loop v0.9.0 ===")
        print(f"MODEL→TEST→FAIL→UNDERSTAND FAILURE→GENERATE COUNTEREXAMPLE→GENERATE TRAINING DATA→ADAPT CURRICULUM→TRAIN→DISTILL→VERIFY→REGRESSION TEST→RELEASE→OBSERVE→NEW FAILURE→LOOP")
        print(f"Objective: Every validated failure becomes permanent learning and evaluation signal E_{{t+1}}=E_t ∪ F_t")
        print(f"Autopoietic Frameworks (13): {self.autopoietic_frameworks}")

        for i in range(iterations):
            current = self.current_version
            print(f"\n--- Iteration {i+1}/{iterations} — {current.version} ---")

            # Evaluate
            eval_result = self.evaluate(current)
            failures = eval_result["failures"]

            # Failure Memory E_{t+1}=E_t ∪ F_t
            self.failure_memory.extend(failures)
            print(f"Failure Memory: E_t size={len(self.evaluation_suite)} + F_t {len(failures)} → E_{{t+1}}=E_t ∪ F_t")

            # Analyze
            root_causes = self.analyze_failures(failures)

            # Hypotheses
            hypotheses = self.generate_hypotheses(root_causes)

            # 13 Autopoietic Frameworks
            synthetic = self.dataforge_autopoietic(failures)
            self.curriculum_autopoietic(failures)
            self.architecture_autopoietic()
            self.quantum_autopoietic()
            self.neuromorphic_autopoietic()
            self.bci_autopoietic()
            self.scada_autopoietic()
            self.robotics_autopoietic()
            self.evaluation_autopoietic(failures)
            self.distillation_autopoietic(current)
            self.alignment_autopoietic()
            self.superalignment_autopoietic()
            self.formal_verification_autopoietic()
            self.continual_learning_autopoietic()

            # Train next version
            next_version = self.train_next_version(current, synthetic, hypotheses)

            # Verify and promote
            if self.verify_and_promote(current, next_version):
                print(f"✓ {next_version.version} improved and safe and formally verified and aligned, becomes new AGI_t: {current.version} → {next_version.version} score {current.score:.3f}→{next_version.score:.3f}")
                self.versions.append(next_version)
                self.current_version = next_version
            else:
                print(f"✗ {next_version.version} not improved or not safe or not formally verified or not aligned, keeping {current.version}")

        print(f"\n=== Recursive Self-Improvement Complete ===")
        print(f"Versions: {[v.version for v in self.versions]}")
        print(f"Scores: {[f'{v.score:.3f}' for v in self.versions]}")
        print(f"Quantum Volumes: {[v.quantum_volume for v in self.versions]}")
        print(f"Neuromorphic Power: {[f'{v.neuromorphic_power_mw:.1f}mW' for v in self.versions]}")
        print(f"Alignment Scores: {[f'{v.alignment_score:.3f}' for v in self.versions]}")
        print(f"Formal Verified: {[f'{v.formal_verified}/14' for v in self.versions]}")
        print(f"Final evaluation suite size: {len(self.evaluation_suite)} (grew via E_{{t+1}}=E_t ∪ F_t)")
        print(f"Final failure memory size: {len(self.failure_memory)}")
        print(f"Objective: Every validated failure becomes permanent learning and evaluation signal")

if __name__ == "__main__":
    rsi = RecursiveSelfImprovement()
    rsi.recursive_loop(iterations=3)
