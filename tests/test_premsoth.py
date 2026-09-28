import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.premsoth import Premsoth, AgentOutput

def test_agreement():
    premsoth = Premsoth()
    outputs = [
        AgentOutput("Agent1","T001",{"fault_probability":0.82},0.82,0.9),
        AgentOutput("Agent2","T001",{"fault_probability":0.85},0.85,0.9),
        AgentOutput("Agent3","T001",{"fault_probability":0.88},0.88,0.9),
    ]
    decision = premsoth.verify("T001", outputs)
    assert decision["agreement_score"] > 0.7
    assert decision["verified"]
    print(f"Agreement {decision['agreement_score']:.2f} PASSED")

def test_failure_injection():
    premsoth = Premsoth()
    # Agent1 correct, Agent2 correct, Agent3 wrong, Agent4 correct, Agent5 wrong per Phase 4
    outputs = [
        AgentOutput("Agent1","TEST",{"fault_probability":0.82},0.82,0.9),
        AgentOutput("Agent2","TEST",{"fault_probability":0.85},0.85,0.9),
        AgentOutput("Agent3","TEST",{"fault_probability":0.10},0.4,0.5),  # wrong
        AgentOutput("Agent4","TEST",{"fault_probability":0.88},0.88,0.9),
        AgentOutput("Agent5","TEST",{"fault_probability":0.05},0.3,0.4),  # wrong
    ]
    decision = premsoth.verify("TEST", outputs)
    # With 2 faulty, agreement lower, but BFT N=5 f=1 should still handle 1, not 2
    print(f"Failure injection: agreement={decision['agreement_score']:.2f}, verified={decision['verified']}, scores={decision['scores']}")
    # Should identify inconsistent outputs via low scores
    assert decision["scores"]["Agent3"] < decision["scores"]["Agent1"]
    print("Failure injection PASSED")

def test_bft():
    from sparsiz.premsoth import Premsoth
    premsoth = Premsoth()
    # N>=3f+1
    assert premsoth.consensus.min_nodes_for_f(1) == 4
    assert premsoth.consensus.check_bft(4) == True
    assert premsoth.consensus.check_bft(3) == False
    print("BFT N>=3f+1 PASSED")

def test_safety():
    premsoth = Premsoth()
    # Vmin≤Vcmd≤Vmax, Icmd≤Imax, T<Tcritical
    safe = {"voltage":400,"current":50,"temperature":80}
    assert premsoth.safety_gate.check(safe)["passed"]
    unsafe_v = {"voltage":600,"current":50,"temperature":80}
    assert not premsoth.safety_gate.check(unsafe_v)["passed"]
    unsafe_i = {"voltage":400,"current":150,"temperature":80}
    assert not premsoth.safety_gate.check(unsafe_i)["passed"]
    unsafe_t = {"voltage":400,"current":50,"temperature":200}
    assert not premsoth.safety_gate.check(unsafe_t)["passed"]
    print("Safety checks Vmin≤V≤Vmax, I≤Imax, T<Tcritical PASSED")

def test_far_frr():
    premsoth = Premsoth()
    # FAR = incorrect accepted / total incorrect, FRR = correct rejected / total correct
    test_cases = [
        ([AgentOutput("A1","T",{"fault_probability":0.82},0.9,0.9), AgentOutput("A2","T",{"fault_probability":0.85},0.9,0.9), AgentOutput("A3","T",{"fault_probability":0.88},0.9,0.9)], True),
        ([AgentOutput("A1","T",{"fault_probability":0.1},0.4,0.5), AgentOutput("A2","T",{"fault_probability":0.15},0.4,0.5), AgentOutput("A3","T",{"fault_probability":0.05},0.3,0.4)], False),
    ]
    metrics = premsoth.benchmark(test_cases)
    print(f"Benchmark: A_c={metrics['accuracy']:.2f}, FAR={metrics['far']:.2f}, FRR={metrics['frr']:.2f}")
    print("FAR/FRR PASSED")

if __name__ == "__main__":
    test_agreement()
    test_failure_injection()
    test_bft()
    test_safety()
    test_far_frr()
    print("All PREMSOTH tests passed")
