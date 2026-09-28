# Contributing to The Last Dance

## Code of Conduct

This is a research prototype for heterogeneous AI compute orchestration. Be respectful, focus on measurable results, no hype claims.

## Principles

1. **No zero-latency / error-free claims** without measurement (mean/median/p95/p99/worst, hardware config, kernel version, workload)
2. **Correct architecture separation**: Control Plane vs Compute Plane, eBPF is instrumentation not bare-metal hypervisor, KVM is virtualization interface, quantum is optional external accelerator
3. **Safety first**: Never AI→PLC without independent safety layer (range checking, interlock, human/authorized controller)
4. **Benchmark against baselines**: Linux default scheduling, round-robin, random, static GPU, traditional orchestration, centralized scheduler
5. **Security**: Policy matrix Ω is policy not crypto; real security via OS perms, capabilities, IOMMU, secure boot, TPM, signatures, isolation

## Development Setup

```bash
# Ubuntu
sudo apt install rustc cargo python3 python3-pip libbpf-dev clang llvm bpftool
pip install torch numpy scipy networkx pyyaml toml pytest prometheus_client

# Build
cargo build --release
pip install -e .

# Test
cargo test
pytest tests/
python3 simulations/compute_grid/simulator.py
python3 examples/motor_fault_e2e.py
```

## Repository Structure

Follow structure in README.md and ARCHITECTURE.md. Each module:

- `core/rajaram/`: RAJARAM Core (Rust) — global state S(t), module lifecycle, permission matrix Ω, security chain, master clock τ(t), state machine, fault isolation
- `kernel/makesh/`: MAKESH (Rust/C) — eBPF telemetry, scheduler cost J_i, thermal, resource policy
- `intelligence/saram/`: SARAM (Python→Rust) — encoder f_θ, decoder g_φ, physics constraints P=VI etc, loss L
- `routing/faisanth/`: FAISANTH (Rust/Python) — graph G=(V,E), cost C_ij, Y=G+jB, Y†, optimizer, task classification
- `verification/premsoth/`: PREMSOTH (Rust) — verification Score_i, BFT N≥3f+1, safety gate Vmin≤V≤Vmax etc
- `hardware/`: HAL trait ComputeDevice, CPU/GPU/NPU/FPGA/Neuromorphic/Quantum devices
- `interfaces/`: BCI, SCADA, OPC-UA, Modbus, MQTT
- `simulations/`: Phase 0 mathematical simulator

## Language Allocation

- RAJARAM Core: Rust
- Bare-metal kernel: Rust + limited assembly
- eBPF: C / Rust tooling
- Hardware drivers: Rust/C
- SARAM: Python → Rust
- AI models: Python/PyTorch
- FAISANTH: Rust/Python
- Numerical: Rust/C++
- PREMSOTH: Rust
- Simulation: Python
- FPGA: Verilog/SystemVerilog
- CUDA: CUDA/C++
- Testing: Python/Rust
- Config: TOML/YAML
- APIs: gRPC/Protobuf

## Pull Request Process

1. Fork, branch from main
2. Implement with tests and benchmarks
3. Update docs if architecture changes
4. Ensure `cargo test` and `pytest` pass
5. Include benchmark numbers: Latency L, Throughput, Energy E, Routing efficiency η_r, Consensus accuracy A_c, FAR/FRR, Isolation latency T_fault→isolation
6. No hype: report measured values, not claims

## Commit Messages

- feat(rajaram): add module lifecycle quarantine
- feat(makesh): implement J_i cost scheduler
- feat(saram): add physics-guided autoencoder P=VI loss
- feat(faisanth): add Y-Bus Y† pseudoinverse routing
- feat(premsoth): add BFT consensus N≥3f+1
- fix(hal): correct CPU affinity handling
- docs(arch): clarify eBPF vs hypervisor
- bench: add FAISANTH vs round-robin comparison

## Testing

- Unit tests per crate
- Integration tests in `tests/`
- Simulations in `simulations/`
- Benchmarks in `benchmarks/` with baseline comparisons
- Safety tests: inject failures, verify PREMSOTH rejects incorrect, safety gate blocks out-of-range commands

## Security

See SECURITY.md. Report vulnerabilities privately. Never allow raw BCI→actuators, never LLM→PLC without safety layer.
