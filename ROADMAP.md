# Roadmap — The Last Dance

## Phase 0 — Mathematical Simulator [DONE V1]
- Compute nodes (10 nodes: CPU-1/2, GPU-1/2, NPU-1/2, FPGA-1, EDGE-1/2/3)
- Y matrix Y=G+jB, Y† pseudoinverse, topology estimation
- Routing: round-robin, random, shortest-path, FAISANTH cost optimization
- Thermal model, latency model, agent graph, consensus
- Success: Demonstrate measurable routing efficiency η_r
- Implementation: `simulations/compute_grid/simulator.py`, `simulations/power_grid/ybus_sim.py`, `simulations/thermal/thermal_model.py`

## Phase 1 — SARAM [DONE V1]
- Dataset: offline EEG (simulated), industrial telemetry (motor vibration, current, temp, RPM, harmonics)
- Preprocessing: filtering, artifact removal, feature extraction
- Encoder: f_θ(x): R^{d_r}→R^{d_z}, d_z<<d_r
- Decoder: g_φ(z): R^{d_z}→R^{d_r}
- Physics loss: P=VI, S=P+jQ, P_mech=Tω, mẍ+cẋ+kx=F(t)
- Loss: L = L_rec + λ1 L_physics + λ2 L_task + λ3 L_reg
- Metrics: CompressionRatio = d_raw/d_latent, reconstruction accuracy, task accuracy
- Implementation: `intelligence/saram/`

## Phase 2 — FAISANTH [DONE V1]
- Create 10 simulated compute nodes with capacity/latency/temperature/energy/reliability
- Task descriptor: {task_id, type, latency_budget_ms, memory_mb, compute_intensity, parallelism, thermal_priority, security_level}
- Cost: C_ij = α L_ij + β E_ij + γ T_ij + δ B_ij^{-1} + ε R_ij
- Optimization: P*=argmin C(P) s.t. Capacity≥Demand, Temp<Tmax, Memory≥M_req
- Compare: Round-robin vs Random vs Shortest-path vs FAISANTH
- Implementation: `routing/faisanth/` (Rust + Python)

## Phase 3 — Multi-Agent System [DONE V1]
- Run Agent 1..5 on different compute resources
- Agents: Physics Agent, ML Agent, Signal Agent, Diagnostic Agent, Reasoning Agent
- Measure latency, throughput, energy, agreement, failure recovery
- Implementation: `examples/multi_agent.py`, `the_last_dance/agents/`

## Phase 4 — PREMSOTH [DONE V1]
- Inject failures: Agent1 correct, Agent2 correct, Agent3 wrong, Agent4 correct, Agent5 wrong
- Verification: Agreement A_ij=sim(a_i,a_j), Confidence C_i, Reliability R_i, Score_i = w_a A_i + w_c C_i + w_r R_i + w_p P_i
- BFT: N≥3f+1
- Safety gate: Vmin≤Vcmd≤Vmax, Icmd≤Imax, T<Tcritical
- Metrics: FAR, FRR, consensus accuracy A_c
- Implementation: `verification/premsoth/` + `the_last_dance/premsoth.py`

## Phase 5 — MAKESH + eBPF [DONE V1 prototype]
- eBPF monitoring: CPU, processes, scheduling, memory, network, thermal
- Telemetry: CPU util/freq/temp/load/ctx switches/cache, GPU util/mem/temp/power/queue, RAM/swap/page faults/NUMA/bandwidth, Network latency/bandwidth/errors, Thermal T_i(t)
- Scheduling model: J_i = w1 L_i + w2 T_i + w3 E_i + w4 U_i + w5 R_i
- Resource policy: CPU affinity, cgroups, GPU selection
- Only after this works experiment with stronger runtime controls
- Implementation: `kernel/makesh/` (eBPF C + Rust loader + Python telemetry)

## Phase 6 — Real Hardware [PARTIAL V1]
- First: CPU, GPU (implemented via HAL)
- Then: NPU, FPGA (stubs + trait)
- Then: neuromorphic (SNN event detection stub)
- Finally: quantum/photonic (optional external accelerator interface, QUBO formulation)
- Implementation: `hardware/`

## Phase 7 — BCI [STUB + SIMULATION]
- Start offline EEG dataset → real-time EEG → SARAM streaming → real-time inference
- No invasive interfaces in V1
- Flow: EEG/BCI→Acquisition→Filtering→Artifact removal→Feature extraction→SARAM→Latent→AI agents
- Never raw BCI→actuators
- Implementation: `interfaces/bci/`, `intelligence/saram/datasets/`

## Phase 8 — Industrial [SIMULATION]
- Lab testbed: Sensor→Raspberry Pi/industrial PC→MQTT/OPC UA→The Last Dance→Simulation
- Simulated PLC before physical machinery
- Flow: PLC→Modbus TCP/OPC UA/MQTT gateway→SARAM→FAISANTH→AI→PREMSOTH→Safety layer→PLC/HMI
- Keep deterministic control independent from AI
- Implementation: `interfaces/scada/`, `interfaces/opcua/`, `interfaces/modbus/`, `interfaces/mqtt/`

## Phase 9 — KVM [DESIGN + STUB]
- RAJARAM VM Manager: VM creation, vCPU allocation, memory allocation, device assignment, VM health
- KVM API: /dev/kvm VM/vCPU/device interfaces
- Implementation: `core/rajaram/kvm/` stub with design doc

## Phase 10 — Custom Kernel [DESIGN DOC]
- Bootloader→Memory→Interrupts→Scheduler→IPC→Drivers→RAJARAM Core→MAKESH→AI runtime
- At this stage call it custom bare-metal execution environment
- Implementation: `docs/architecture/bare_metal.md` + `kernel/bare_metal/` design

## Phase 11 — Bare Metal [LONG TERM]
- RAJARAM MICROKERNEL: GDT/IDT, Page Tables, Interrupt Controller, Scheduler, Memory Manager, IPC, Capability Manager, DMA Manager, IOMMU, Device Drivers, Accelerator Runtime
- Final architecture: APPLICATIONS→PREMSOTH→FAISANTH→SARAM→MAKESH→RAJARAM MICROKERNEL→HAL→Devices

## V1 Success Criteria

Demonstrate:

```
Real Sensor Data → SARAM → FAISANTH → Multiple AI Agents → PREMSOTH → RAJARAM
                    ↑
              MAKESH continuously observes underlying hardware
```

With measurable:

- CompressionRatio, reconstruction accuracy
- Routing efficiency η_r vs baselines
- Consensus accuracy A_c, FAR, FRR
- Latency breakdown L_total = L_ingest+L_encode+L_route+L_execute+L_verify+L_authorize
- Isolation latency mean/median/p95/p99
- Throughput, energy, thermal

No claims of zero latency, error-free, <15μs without measurement.

## Release Plan

- v0.1.0: Phase 0 simulator
- v0.2.0: Phase 1 SARAM
- v0.3.0: Phase 2 FAISANTH + Y-Bus
- v0.4.0: Phase 3 Multi-Agent + Phase 4 PREMSOTH
- v0.5.0: Phase 5 MAKESH + eBPF
- v0.6.0: V1 Prototype End-to-End (this release)
- v0.7.0: Hardware HAL CPU/GPU real
- v0.8.0: BCI + Industrial interfaces
- v0.9.0: KVM integration
- v1.0.0: Stable research prototype with benchmarks
- v2.0.0+: Custom kernel exploration

## Contributing

See CONTRIBUTING.md. Each phase needs benchmarks against baselines.
