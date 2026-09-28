# Benchmarking Framework

## Need hard numbers

Measure:

- Latency: L = t_finish - t_start
- Throughput: Throughput = N_tasks / T
- Energy: E = ∫ P(t) dt
- Thermal: T_max
- Memory: M_peak
- Routing efficiency: η_r = C_baseline / C_FAISANTH
- Consensus accuracy: A_c = correct decisions / total decisions

## Baseline Comparisons

Compare The Last Dance against:

- Linux default scheduling
- Round-robin task routing
- Random agent routing
- Static GPU assignment
- Traditional multi-agent orchestration
- Centralized scheduler

Then demonstrate measurable improvement where it actually exists.

Do not claim superiority before benchmarking.

## What "Zero Latency" Should Become

Never use: zero latency

Use: low-latency, bounded execution

Define:

```
L_total = L_ingest + L_encode + L_route + L_execute + L_verify + L_authorize
```

Then benchmark every component.

## What "Error-Free" Should Become

Never claim: error-free consensus

Use: fault-aware verification with measurable false-accept and false-reject rates

Define:

```
FAR = incorrect outputs accepted / total incorrect outputs
FRR = correct outputs rejected / total correct outputs
```

## What "<15 μs" Should Become

Do not publish: memory access revoked in <15 μs until you have measured it.

Use:

```
T_fault→isolation
```

and report:

- mean
- median
- p95
- p99
- worst observed
- hardware configuration
- kernel version
- workload

Example:

```
Isolation latency:
median = X μs
p95    = X μs
p99    = X μs
```

## Observability

Every subsystem needs telemetry.

- RAJARAM: health, security, state
- MAKESH: CPU, GPU, memory, thermal
- SARAM: input rate, compression, reconstruction
- FAISANTH: routing, latency, resource utilization
- PREMSOTH: agreement, failures, rejected outputs

Use: Prometheus, Grafana, OpenTelemetry, structured logs for prototype.
