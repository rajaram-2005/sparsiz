# Hardware Abstraction Layer

## Common Interface

```rust
trait ComputeDevice {
    fn initialize(&mut self);
    fn capabilities(&self) -> Capabilities;
    fn allocate(&mut self, request: ComputeRequest);
    fn execute(&mut self, task: Task);
    fn release(&mut self);
    fn telemetry(&self) -> Telemetry;
}
```

Implement:

- CPUDevice
- GPUDevice
- NPUDevice
- FPGADevice
- NeuromorphicDevice
- QuantumDevice

Initially CPUDevice, GPUDevice enough.

## Device Selection

```
What is the task?
       ↓
What hardware can execute it?
       ↓
What hardware is available?
       ↓
What is its latency?
       ↓
What is its thermal state?
       ↓
What is its energy cost?
       ↓
What is its reliability?
       ↓
SELECT
```

## Quantum Integration

Do not implement NP-hard → Quantum automatically.

Instead:

```
Task classifier
      ↓
Is problem quantum-suitable?
      │
   ┌──┴──┐
   │     │
  NO    YES
   │     │
 CPU/GPU  Quantum backend
```

Research targets: combinatorial optimization, QUBO, scheduling, sampling, quantum chemistry.

FAISANTH should select quantum only when problem formulation and available backend justify it.

## Neuromorphic Integration

MAKESH can expose NeuromorphicDevice with workloads:

- event detection
- spiking neural networks
- low-power anomaly detection
- temporal pattern recognition

Flow:

```
Event stream
     ↓
SNN representation
     ↓
Neuromorphic accelerator
     ↓
Event classification
     ↓
PREMSOTH
```
