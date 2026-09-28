# Security Policy — The Last Dance

## Architecture

```
Secure Boot
    ↓
   TPM
    ↓
RAJARAM Identity
    ↓
┌────────┴────────┐
Module Identity  Resource Policy
    └──────┬──────┘
           ↓
     Authorization
           ↓
    Execution Token
```

Future quantum-resistant: NIST FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA

## Permission Matrix Ω

Ω∈{0,1}^{M×R}, M modules, R resources. Example:

| Module   | CPU | GPU | BCI | PLC | Actuator |
|----------|-----|-----|-----|-----|----------|
| SARAM    | 1   | 1   | 1   | 0   | 0        |
| MAKESH   | 1   | 1   | 0   | 0   | 0        |
| FAISANTH | 1   | 1   | 0   | 0   | 0        |
| PREMSOTH | 1   | 1   | 0   | 0   | 1        |

This matrix is **policy, not cryptography**. Real security via OS permissions, capabilities, memory protection, IOMMU, secure boot, TPM, cryptographic signatures, process isolation.

## Threats

- malicious agent
- compromised model
- memory corruption
- privilege escalation
- malicious sensor
- fake telemetry
- network attack
- model poisoning
- prompt injection
- unauthorized actuator command

## Protection

- secure boot
- TPM
- process isolation
- IOMMU
- capabilities
- signed modules
- encrypted IPC (TLS, mTLS for gRPC)
- authentication
- authorization
- audit logs
- rate limiting
- safety interlocks

## Security Execution Chain

```
REQUEST
  ↓
IDENTITY
  ↓
AUTHENTICATION
  ↓
AUTHORIZATION
  ↓
TASK POLICY
  ↓
FAISANTH ROUTING
  ↓
AGENT EXECUTION
  ↓
PREMSOTH VERIFICATION
  ↓
SAFETY CHECK
  ↓
RAJARAM SIGNATURE
  ↓
EXECUTION
```

## Safety-Critical Execution

Never:

```
LLM → PREMSOTH → PLC
```

Correct:

```
AI recommendation → PREMSOTH → Safety policy engine → Range checking → Interlock checking → Human/authorized controller → PLC
```

Range checks: Vmin≤Vcommand≤Vmax, Icommand≤Imax, T<Tcritical

BCI: Never raw BCI signals→actuators. Flow: EEG/BCI→Acquisition→Filtering→Artifact removal→Feature extraction→SARAM→Latent→AI agents

Industrial: Keep deterministic control logic independent from AI. Flow: PLC→Modbus TCP/OPC UA/MQTT gateway→SARAM→FAISANTH→AI→PREMSOTH→Safety layer→PLC/HMI

## Fault Isolation

Define measurable requirement: T_isolation < T_max

Benchmark stages:

```
fault detected → permission revoked → process stopped → memory isolated → device access removed
```

Measure every stage. If using HW-enforced isolation investigate IOMMU/page tables/memory protection/PCIe isolation/DMA protection/TPM/secure boot.

Report: mean/median/p95/p99/worst observed/hardware config/kernel version/workload. Do NOT claim <15μs without measurement.

## Reporting Vulnerabilities

Do NOT open public issue for security vulnerabilities. Contact maintainers privately.

Provide:

- Description
- Impact (which plane: Hardware/Kernel/Runtime/Intelligence/Verification/Control)
- Reproduction steps
- Suggested mitigation

We will acknowledge within 48h and provide fix timeline.

## Secure Development

- All modules signed
- IPC encrypted
- Audit logs for authorization decisions
- Rate limiting on APIs
- Input validation on all telemetry
- Physics consistency checks as additional validation layer
- BFT consensus N≥3f+1 for critical decisions

## Dependencies

- Rust crates audited via cargo audit
- Python dependencies pinned, check via pip-audit
- eBPF programs verified by kernel verifier
- Container images scanned

## PQC Readiness

NIST finalized standards:

- ML-KEM (FIPS 203) for key encapsulation
- ML-DSA (FIPS 204) for signatures
- SLH-DSA (FIPS 205) for stateless hash-based signatures

RAJARAM Identity should be prepared to migrate to ML-DSA/SLH-DSA for module signatures.

## Observability for Security

- RAJARAM: health/security/state + audit logs
- MAKESH: CPU/GPU/memory/thermal + anomaly detection
- PREMSOTH: agreement/failures/rejected outputs
- Use Prometheus/Grafana/OpenTelemetry/structured logs
- Alert on: permission violations, consensus failures, safety gate rejections, thermal anomalies, unexpected module behavior
