"""
PREMSOTH — Deterministic verification and authorization layer
Not hallucination eliminator — no general architecture guarantees elimination.
Task → Agents A/B/C → Outputs → PREMSOTH → Semantic/Physics/Policy checks → Decision
a_i=f_i(x), Agreement A_ij=sim(a_i,a_j), Confidence C_i=P(a_i|x), Reliability R_i historical
Score_i = w_a A_i + w_c C_i + w_r R_i + w_p P_i
BFT: N>=3f+1, proposal/validation/voting/quorum/commit/reject
Safety: AI→PREMSOTH→Safety policy→Range→Interlock→Human/authorized controller→PLC
Vmin≤Vcmd≤Vmax, Icmd≤Imax, T<Tcritical
FAR, FRR, consensus accuracy A_c
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json
import math

@dataclass
class AgentOutput:
    agent_id: str
    task_id: str
    output: Any
    confidence: float
    reliability: float
    timestamp: int = 0

    def to_dict(self):
        return {"agent_id": self.agent_id, "task_id": self.task_id, "output": self.output, "confidence": self.confidence, "reliability": self.reliability}

@dataclass
class VerificationConfig:
    w_agreement: float = 0.35
    w_confidence: float = 0.25
    w_reliability: float = 0.2
    w_physics: float = 0.2
    min_agents: int = 3
    similarity_threshold: float = 0.7

@dataclass
class SafetyLimits:
    v_min: float = 0.0
    v_max: float = 480.0
    i_max: float = 100.0
    t_critical: float = 150.0
    actuator_min: float = -100.0
    actuator_max: float = 100.0

class Validator:
    def __init__(self, config: VerificationConfig):
        self.config = config

    def similarity(self, a: AgentOutput, b: AgentOutput) -> float:
        # Structured output comparison
        if isinstance(a.output, dict) and isinstance(b.output, dict):
            if "fault_probability" in a.output and "fault_probability" in b.output:
                fa = a.output["fault_probability"]
                fb = b.output["fault_probability"]
                return 1.0 - abs(fa-fb)
            if a.output == b.output:
                return 1.0
            return 0.5
        else:
            return 1.0 if a.output == b.output else 0.3

    def physics_consistency(self, output: AgentOutput) -> float:
        if isinstance(output.output, dict):
            if "voltage" in output.output:
                v = output.output["voltage"]
                if v<0 or v>1000:
                    return 0.0
            if "temperature" in output.output:
                t = output.output["temperature"]
                if t>200:
                    return 0.2
        return 1.0

    def validate(self, outputs: List[AgentOutput]) -> Dict:
        agreements = []
        total_sim = 0
        count = 0
        for i in range(len(outputs)):
            for j in range(i+1, len(outputs)):
                sim = self.similarity(outputs[i], outputs[j])
                total_sim += sim
                count += 1
                agreements.append({"agent_i": outputs[i].agent_id, "agent_j": outputs[j].agent_id, "similarity": sim})

        overall = total_sim / count if count>0 else 0.0
        avg_conf = sum(o.confidence for o in outputs) / len(outputs) if outputs else 0.0

        scores = {}
        for out in outputs:
            # A_i average agreement
            a_i_vals = [a["similarity"] for a in agreements if a["agent_i"]==out.agent_id or a["agent_j"]==out.agent_id]
            a_i = sum(a_i_vals)/len(a_i_vals) if a_i_vals else 0.0
            c_i = out.confidence
            r_i = out.reliability
            p_i = self.physics_consistency(out)
            score = self.config.w_agreement*a_i + self.config.w_confidence*c_i + self.config.w_reliability*r_i + self.config.w_physics*p_i
            scores[out.agent_id] = score

        return {"agreements": agreements, "overall_agreement": overall, "avg_confidence": avg_conf, "scores": scores, "physics_consistent": True}

class BftConsensus:
    def __init__(self, f_tolerated: int = 1, quorum_ratio: float = 0.66):
        self.f_tolerated = f_tolerated
        self.quorum_ratio = quorum_ratio

    def min_nodes_for_f(self, f: int) -> int:
        return 3*f+1

    def check_bft(self, n: int) -> bool:
        return n >= self.min_nodes_for_f(self.f_tolerated)

    def value_similarity(self, a, b) -> float:
        if a==b:
            return 1.0
        if isinstance(a, (int,float)) and isinstance(b, (int,float)):
            return 1.0 - min(abs(a-b),1.0)
        return 0.5

    def reach_consensus(self, outputs: List[AgentOutput], validation: Dict) -> Dict:
        n = len(outputs)
        bft_valid = self.check_bft(n)

        # Proposal: highest Score_i
        best_id = max(validation["scores"], key=lambda k: validation["scores"][k]) if validation["scores"] else None
        agreed_value = None
        if best_id:
            for o in outputs:
                if o.agent_id==best_id:
                    agreed_value = o.output
                    break

        votes = []
        if agreed_value is not None:
            for o in outputs:
                sim = self.value_similarity(o.output, agreed_value) if not isinstance(o.output, dict) else (1.0 if o.output==agreed_value else 0.5)
                # For dict with fault_probability
                if isinstance(o.output, dict) and isinstance(agreed_value, dict) and "fault_probability" in o.output and "fault_probability" in agreed_value:
                    sim = 1.0 - abs(o.output["fault_probability"]-agreed_value["fault_probability"])
                vote = sim>=0.7
                votes.append({"agent_id": o.agent_id, "vote": vote, "value": o.output})

        positive = sum(1 for v in votes if v["vote"])
        quorum_needed = math.ceil(n * self.quorum_ratio)
        quorum_reached = positive >= quorum_needed
        commit = quorum_reached and bft_valid

        reason = f"Quorum {positive}/{n} needed {quorum_needed}, BFT valid={bft_valid} (N>=3f+1={self.min_nodes_for_f(self.f_tolerated)})"

        return {"agreed_value": agreed_value, "votes": votes, "quorum_reached": quorum_reached, "commit": commit, "reason": reason, "bft_valid": bft_valid}

class SafetyGate:
    def __init__(self, limits: Optional[SafetyLimits] = None):
        self.limits = limits or SafetyLimits()

    def check(self, output: Any) -> Dict:
        checks = []
        passed = True
        reasons = []

        if isinstance(output, dict):
            # Vmin≤Vcmd≤Vmax
            v = output.get("voltage") or output.get("V_command") or output.get("v_command")
            if v is not None:
                ok = self.limits.v_min <= v <= self.limits.v_max
                checks.append((f"Voltage {v} in [{self.limits.v_min},{self.limits.v_max}]", ok))
                if not ok:
                    passed=False
                    reasons.append(f"Voltage {v} out of range")

            # Icmd≤Imax
            i = output.get("current") or output.get("I_command")
            if i is not None:
                ok = i <= self.limits.i_max
                checks.append((f"Current {i} ≤ {self.limits.i_max}", ok))
                if not ok:
                    passed=False
                    reasons.append(f"Current {i} exceeds Imax")

            # T<Tcritical
            t = output.get("temperature")
            if t is not None:
                ok = t < self.limits.t_critical
                checks.append((f"Temperature {t} < {self.limits.t_critical}", ok))
                if not ok:
                    passed=False
                    reasons.append(f"Temperature {t} exceeds Tcritical")

            # Actuator
            a = output.get("actuator_command") or output.get("actuator")
            if a is not None:
                ok = self.limits.actuator_min <= a <= self.limits.actuator_max
                checks.append((f"Actuator {a} in [{self.limits.actuator_min},{self.limits.actuator_max}]", ok))
                if not ok:
                    passed=False
                    reasons.append(f"Actuator {a} out of range")

            if not checks:
                return {"passed": True, "reason": "No safety-critical command, not applicable", "checks": []}

        else:
            return {"passed": True, "reason": "No safety-critical command", "checks": []}

        if passed:
            return {"passed": True, "reason": "All safety checks passed: Vmin≤Vcmd≤Vmax, Icmd≤Imax, T<Tcritical", "checks": checks}
        else:
            return {"passed": False, "reason": "; ".join(reasons), "checks": checks}

class Premsoth:
    def __init__(self, config: Optional[VerificationConfig] = None):
        self.config = config or VerificationConfig()
        self.validator = Validator(self.config)
        self.consensus = BftConsensus()
        self.safety_gate = SafetyGate()

    def verify(self, task_id: str, outputs: List[AgentOutput]) -> Dict:
        if len(outputs) < self.config.min_agents:
            return {
                "task_id": task_id,
                "agreed_output": None,
                "confidence": 0.0,
                "agreement_score": 0.0,
                "scores": {},
                "verified": False,
                "reason": f"Insufficient agents {len(outputs)} < {self.config.min_agents}",
                "consensus": {"quorum_reached": False, "reason": "insufficient agents"},
                "safety_check": {"passed": False, "reason": "insufficient agents"},
            }

        validation = self.validator.validate(outputs)
        consensus = self.consensus.reach_consensus(outputs, validation)

        safety_check = self.safety_gate.check(consensus["agreed_value"]) if consensus["agreed_value"] else {"passed": False, "reason": "No agreed value"}

        verified = validation["overall_agreement"] >= self.config.similarity_threshold and consensus["quorum_reached"] and safety_check["passed"]

        reason = f"Verified: agreement={validation['overall_agreement']:.2f}, quorum={consensus['quorum_reached']}, safety={safety_check['passed']}" if verified else f"Rejected: agreement={validation['overall_agreement']:.2f} threshold {self.config.similarity_threshold}, quorum={consensus['quorum_reached']}, safety={safety_check['passed']} - {safety_check['reason']}"

        return {
            "task_id": task_id,
            "agreed_output": consensus["agreed_value"],
            "confidence": validation["avg_confidence"],
            "agreement_score": validation["overall_agreement"],
            "scores": validation["scores"],
            "verified": verified,
            "reason": reason,
            "consensus": consensus,
            "safety_check": safety_check,
            "validation": validation,
        }

    def benchmark(self, test_cases: List[Tuple[List[AgentOutput], bool]]) -> Dict:
        correct=0
        false_accept=0
        false_reject=0
        total_incorrect=0
        total_correct=0

        for outputs, should_be_valid in test_cases:
            decision = self.verify("BENCH", outputs)
            if decision["verified"]==should_be_valid:
                correct+=1
            if should_be_valid:
                total_correct+=1
                if not decision["verified"]:
                    false_reject+=1
            else:
                total_incorrect+=1
                if decision["verified"]:
                    false_accept+=1

        return {
            "total_cases": len(test_cases),
            "correct_decisions": correct,
            "accuracy": correct/len(test_cases) if test_cases else 0,  # A_c
            "far": false_accept/total_incorrect if total_incorrect>0 else 0.0,
            "frr": false_reject/total_correct if total_correct>0 else 0.0,
            "false_accept": false_accept,
            "false_reject": false_reject,
        }

# Example agents per spec Phase 4: inject failures
def example_agents_motor_fault():
    # Agent 1 correct, Agent 2 correct, Agent 3 wrong, Agent 4 correct, Agent 5 wrong
    return [
        AgentOutput("PhysicsAgent","MOTOR_001",{"fault_probability":0.82,"voltage":400,"temperature":81},0.82,0.9),
        AgentOutput("MLAgent","MOTOR_001",{"fault_probability":0.91,"voltage":400,"temperature":81},0.91,0.95),
        AgentOutput("SignalAgent","MOTOR_001",{"fault_probability":0.15,"voltage":400,"temperature":81},0.4,0.6),  # wrong
        AgentOutput("DiagnosticAgent","MOTOR_001",{"fault_probability":0.88,"voltage":400,"temperature":81},0.88,0.92),
        AgentOutput("FaultyAgent","MOTOR_001",{"fault_probability":0.05,"voltage":900,"temperature":81},0.3,0.5),  # wrong + out of range voltage
    ]

if __name__ == "__main__":
    premsoth = Premsoth()
    outputs = example_agents_motor_fault()
    decision = premsoth.verify("MOTOR_001", outputs)
    print(f"Verified: {decision['verified']}, reason: {decision['reason']}")
    print(f"Agreement: {decision['agreement_score']:.2f}, Confidence: {decision['confidence']:.2f}")
    print(f"Scores: {decision['scores']}")
    print(f"Consensus: {decision['consensus']['reason']}")
    print(f"Safety: {decision['safety_check']}")
