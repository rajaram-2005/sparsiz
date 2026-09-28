"""
Phase 0 — Mathematical Simulator: compute nodes, Y matrix, routing, thermal, latency, agent graph, consensus
No hardware required
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from sparsiz.faisanth import Faisanth, TaskDescriptor
from sparsiz.makesh import Makesh
from sparsiz.premsoth import Premsoth, AgentOutput
from sparsiz.saram import Saram, SaramConfig
from sparsiz.hal import HAL, ComputeRequest, Task

def simulate_compute_grid():
    print("=== Phase 0: Compute Grid Simulator ===")
    faisanth = Faisanth()
    print(faisanth.ybus.display())
    print(faisanth.ybus.topology_estimation())

    try:
        pinv = faisanth.ybus.pseudoinverse()
        print(f"Y† pseudoinverse computed: type={type(pinv)}")
    except Exception as e:
        print(f"Y† failed (expected without numpy): {e}")

    tasks = [
        TaskDescriptor.example(),
        TaskDescriptor.motor_fault(),
        TaskDescriptor.bci(),
        TaskDescriptor("T002","inference",30,2048,0.5,0.4,0.5,2),
        TaskDescriptor("T003","training",100,8192,0.95,0.95,0.3,3),
    ]

    for task in tasks:
        route = faisanth.route(task)
        print(f"Task {task.task_id} ({task.task_type}) -> {route['nodes']} cost={route['total_cost']:.4f} latency={route['latency_ms']}ms meets={route['meets_constraints']} device={route['device_type']}")

    bench = faisanth.benchmark_vs_baselines(tasks)
    print("\n=== Benchmark vs Baselines ===")
    print(f"FAISANTH avg cost: {bench['faisanth_avg']:.4f}")
    print(f"Round-robin avg: {bench['round_robin_avg']:.4f} efficiency η_r={bench['efficiency_vs_rr']:.2f} = C_baseline/C_FAISANTH")
    print(f"Random avg: {bench['random_avg']:.4f} η_r={bench['efficiency_vs_random']:.2f}")
    print(f"Shortest-path avg: {bench['shortest_path_avg']:.4f} η_r={bench['efficiency_vs_shortest']:.2f}")

    # MAKESH
    print("\n=== MAKESH Telemetry ===")
    makesh = Makesh()
    tel = makesh.get_telemetry()
    print(f"CPU util={tel.cpu.utilization:.2f} temp={tel.cpu.temperature_c}°C freq={tel.cpu.frequency_mhz}MHz")
    print(f"GPU util={tel.gpu.utilization:.2f} mem={tel.gpu.memory_used_mb}/{tel.gpu.memory_total_mb}MB temp={tel.gpu.temperature_c}°C power={tel.gpu.power_w}W queue={tel.gpu.queue_utilization}")
    print(f"Memory RAM={tel.memory.ram_used_mb}/{tel.memory.ram_total_mb}MB swap={tel.memory.swap_used_mb}MB page_faults={tel.memory.page_faults} NUMA={tel.memory.numa_locality} BW={tel.memory.bandwidth_gbps}Gbps")
    print(f"Network latency={tel.network.latency_ms}ms packet_rate={tel.network.packet_rate} BW={tel.network.bandwidth_mbps}Mbps errors={tel.network.errors}")
    print(f"Thermal T_i(t): {tel.thermal}")
    print(f"eBPF programs: {makesh.ebpf_programs()}")
    copy, zero = makesh.telemetry.benchmark_copy_vs_zerocopy()
    print(f"Benchmark: Latency_copy={copy}μs vs Latency_zero-copy={zero}μs")

    # SARAM
    print("\n=== SARAM Compression ===")
    saram = Saram(SaramConfig(raw_dim=128, latent_dim=16))
    from sparsiz.saram import IndustrialDataset
    raw = IndustrialDataset.motor_example()
    latent, meta = saram.encode(raw)
    print(f"Raw {raw}")
    print(f"Compressed {meta['raw_dim']} -> {meta['latent_dim']} ratio={meta['compression_ratio']:.1f} rec_err={meta['reconstruction_error']:.4f} physics={meta['physics_consistency']:.2f}")
    print(f"L_total breakdown: L_ingest+L_encode+L_route+L_execute+L_verify+L_authorize (simulated)")

    # PREMSOTH
    print("\n=== PREMSOTH Verification ===")
    premsoth = Premsoth()
    outputs = [
        AgentOutput("PhysicsAgent","MOTOR_001",{"fault_probability":0.82,"voltage":400,"temperature":81},0.82,0.9),
        AgentOutput("MLAgent","MOTOR_001",{"fault_probability":0.91,"voltage":400,"temperature":81},0.91,0.95),
        AgentOutput("SignalAgent","MOTOR_001",{"fault_probability":0.88,"voltage":400,"temperature":81},0.88,0.92),
        AgentOutput("DiagnosticAgent","MOTOR_001",{"fault_probability":0.85,"voltage":400,"temperature":81},0.85,0.9),
        AgentOutput("ReasoningAgent","MOTOR_001",{"fault_probability":0.90,"voltage":400,"temperature":81},0.90,0.93),
    ]
    decision = premsoth.verify("MOTOR_001", outputs)
    print(f"Verified: {decision['verified']}, agreement={decision['agreement_score']:.2f}, confidence={decision['confidence']:.2f}")
    print(f"Scores: {decision['scores']}")
    print(f"Consensus: {decision['consensus']['reason']}")
    print(f"Safety: {decision['safety_check']}")

    # Inject failures per Phase 4
    print("\n=== PREMSOTH Failure Injection (Phase 4) ===")
    faulty_outputs = [
        AgentOutput("Agent1","TEST",{"fault_probability":0.82},0.82,0.9),
        AgentOutput("Agent2","TEST",{"fault_probability":0.85},0.85,0.9),
        AgentOutput("Agent3","TEST",{"fault_probability":0.10},0.4,0.5),  # wrong
        AgentOutput("Agent4","TEST",{"fault_probability":0.88},0.88,0.9),
        AgentOutput("Agent5","TEST",{"fault_probability":0.05},0.3,0.4),  # wrong
    ]
    decision2 = premsoth.verify("TEST", faulty_outputs)
    print(f"With 2 faulty agents: verified={decision2['verified']}, agreement={decision2['agreement_score']:.2f}")
    print(f"Scores: {decision2['scores']}")
    print(f"BFT: N=5, f=1 tolerated? N>=3f+1 => 5>=4 True, should tolerate 1 Byzantine, but 2 faulty -> lower agreement")

    # HAL
    print("\n=== HAL Devices ===")
    hal = HAL()
    for tel in hal.list_telemetry():
        print(f"{tel.device_id}: util={tel.utilization:.2f} temp={tel.temperature_c}°C power={tel.power_w}W mem={tel.memory_used_mb}MB")

    # Benchmarks
    print("\n=== Benchmark Framework ===")
    print("Latency L=t_finish-t_start")
    print("Throughput=N_tasks/T")
    print("Energy E=∫P(t)dt")
    print("Thermal T_max")
    print("Memory M_peak")
    print("Routing efficiency η_r=C_baseline/C_FAISANTH")
    print("Consensus accuracy A_c=correct/total")
    print("Isolation latency T_fault→isolation mean/median/p95/p99/worst")

def main():
    simulate_compute_grid()

if __name__ == "__main__":
    main()
