import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.faisanth import Faisanth, TaskDescriptor, ComputeGraph, YBus

def test_graph():
    graph = ComputeGraph.default_10_nodes()
    assert len(graph.nodes) == 10
    assert len(graph.edges) >= 5
    print("Graph 10 nodes PASSED")

def test_ybus():
    graph = ComputeGraph.default_10_nodes()
    ybus = YBus(graph)
    assert ybus.n == 10
    print(ybus.display())
    print(f"Y-Bus {ybus.n}x{ybus.n} PASSED")
    print(ybus.topology_estimation())

def test_routing():
    faisanth = Faisanth()
    task = TaskDescriptor.motor_fault()
    route = faisanth.route(task)
    assert "nodes" in route
    assert route["total_cost"] < float('inf')
    print(f"Routing {task.task_id} -> {route['nodes']} cost={route['total_cost']:.4f} PASSED")

def test_cost_function():
    faisanth = Faisanth()
    # C_ij = α L_ij + β E_ij + γ T_ij + δ B_ij^{-1} + ε R_ij
    cost = faisanth.edge_cost(latency_ms=10, energy=0.5, thermal=60, bandwidth_gbps=10, reliability=0.9)
    assert cost > 0
    print(f"Cost function C_ij={cost:.4f} PASSED")

    # J_i = w1 L_i + w2 T_i + w3 E_i + w4 U_i + w5 R_i
    from sparsiz.makesh import Scheduler
    sched = Scheduler()
    j = sched.nodes[0].compute_j(sched.weights)
    assert j>0
    print(f"J_i cost={j:.4f} PASSED")

def test_benchmark():
    faisanth = Faisanth()
    tasks = [TaskDescriptor.example(), TaskDescriptor.motor_fault()]
    bench = faisanth.benchmark_vs_baselines(tasks)
    assert bench["efficiency_vs_rr"] > 0
    print(f"Benchmark η_r vs RR={bench['efficiency_vs_rr']:.2f} PASSED")

if __name__ == "__main__":
    test_graph()
    test_ybus()
    test_routing()
    test_cost_function()
    test_benchmark()
    print("All FAISANTH tests passed")
