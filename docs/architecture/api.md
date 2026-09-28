# API Architecture

## RAJARAM

- POST /module/register
- POST /module/start
- POST /module/stop
- POST /permission/request
- GET /system/state
- GET /health

Example:

```json
POST /module/register
{
  "name": "SARAM",
  "path": "intelligence/saram",
  "version": "0.6.0"
}

GET /system/state
{
  "S(t)": [C(t), M(t), G(t), T(t), N(t), A(t), H(t)],
  "timestamp": 17382219
}

GET /health
{
  "core_id": "uuid",
  "state": "READY",
  "modules": ["MAKESH","SARAM","FAISANTH","PREMSOTH"],
  "faults": [],
  "uptime": 3600
}
```

## SARAM

- POST /encode
- POST /decode
- POST /stream

```json
POST /encode
{
  "vibration": 8.3,
  "current": 14.2,
  "temperature": 81,
  "rpm": 1480
}

Response:
{
  "latent": [0.1, 0.2, ...],
  "compression_ratio": 8.0,
  "reconstruction_error": 0.01,
  "physics_consistency": 0.95
}
```

## FAISANTH

- POST /route
- POST /node/register
- POST /node/telemetry
- GET /topology

```json
POST /route
{
  "task_id": "T001",
  "type": "inference",
  "latency_budget_ms": 20,
  "memory_mb": 4096,
  "compute_intensity": 0.84,
  "parallelism": 0.91,
  "thermal_priority": 0.7,
  "security_level": 4
}

Response:
{
  "nodes": ["NPU-1"],
  "total_cost": 0.0238,
  "latency_ms": 4.0,
  "meets_constraints": true,
  "ybus_info": "Topology estimated: 10 nodes"
}
```

## PREMSOTH

- POST /verify
- POST /consensus
- POST /safety-check

```json
POST /verify
{
  "task_id": "MOTOR_001",
  "outputs": [
    {"agent_id": "PhysicsAgent", "output": {"fault_probability": 0.82}, "confidence": 0.82, "reliability": 0.9},
    {"agent_id": "MLAgent", "output": {"fault_probability": 0.91}, "confidence": 0.91, "reliability": 0.95}
  ]
}

Response:
{
  "verified": true,
  "agreement_score": 0.95,
  "confidence": 0.87,
  "scores": {"PhysicsAgent": 0.91, "MLAgent": 0.95},
  "consensus": {"quorum_reached": true, "reason": "Quorum 2/2"},
  "safety_check": {"passed": true}
}
```

## IPC

- High-speed local: shared memory, ring buffers, eventfd, memfd, io_uring
- Kernel↔userspace telemetry: eBPF maps, ring buffers, perf buffers
- Distributed nodes: gRPC, QUIC, NATS, ZeroMQ

Do not force every subsystem to use one communication technology.

## Observability

Prometheus, Grafana, OpenTelemetry, structured logs
