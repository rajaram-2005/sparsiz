# Threat Model

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
- encrypted IPC
- authentication
- authorization
- audit logs
- rate limiting
- safety interlocks

## Execution Chain

```
REQUEST → IDENTITY → AUTHENTICATION → AUTHORIZATION → TASK POLICY → FAISANTH ROUTING → AGENT EXECUTION → PREMSOTH VERIFICATION → SAFETY CHECK → RAJARAM SIGNATURE → EXECUTION
```

## Safety-Critical

Never LLM→PREMSOTH→PLC without independent safety layer

Correct:

```
AI recommendation → PREMSOTH → Safety policy engine → Range checking → Interlock checking → Human/authorized controller → PLC
```

Range: Vmin≤Vcommand≤Vmax, Icommand≤Imax, T<Tcritical

BCI: Never raw BCI→actuators

Industrial: Keep deterministic control independent from AI

## PQC

NIST finalized: ML-KEM FIPS 203, ML-DSA FIPS 204, SLH-DSA FIPS 205
