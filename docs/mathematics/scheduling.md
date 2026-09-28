# Scheduling Mathematics

## MAKESH Scheduling Model

Instead of claiming exact core selection, define cost function.

```
J_i = w1 L_i + w2 T_i + w3 E_i + w4 U_i + w5 R_i
```

where:
- L_i = latency
- T_i = thermal cost
- E_i = energy cost
- U_i = utilization
- R_i = reliability penalty

Choose:

```
i* = argmin_i J_i
```

This is implementable.

## FAISANTH Cost Function

For edge i,j:

```
C_ij = α L_ij + β E_ij + γ T_ij + δ B_ij^{-1} + ε R_ij
```

Then route:

```
P* = argmin_P C(P)
```

subject to:

```
Capacity_i >= Demand_i
Temperature_i < T_max
Memory_i >= M_required
```

## Task Classification

Every incoming task gets descriptor:

```json
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
```

Then FAISANTH determines: CPU? GPU? NPU? FPGA? Neuromorphic? External accelerator? Multiple agents?

## Device Selection Flow

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

## Benchmarking

```
Latency: L = t_finish - t_start
Throughput: N_tasks / T
Energy: E = ∫ P(t) dt
Routing efficiency: η_r = C_baseline / C_FAISANTH
```

Compare against: Linux default scheduling, round-robin, random, static GPU, traditional orchestration, centralized scheduler.
