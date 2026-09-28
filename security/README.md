# Security Fabric

SECURITY ROOT
  ├── Authentication, Authorization → Capability → Isolation → Execution

Audit Fabric: Every significant operation records timestamp, request ID, module, model, agent, hardware, input hash, output hash, decision, authorization, failure → reproducibility and forensic analysis

Execution modes:
MODE 0 AIR-GAPPED
MODE 1 LOCAL ONLY
MODE 2 LOCAL+LAN
MODE 3 LOCAL+APPROVED CLOUD
MODE 4 DISTRIBUTED HYBRID
Policy controls whether network access is permitted.
