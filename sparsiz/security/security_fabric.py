"""
SECURITY FABRIC

SECURITY ROOT
  ├── Authentication, Authorization → Capability → Isolation → Execution

Audit Fabric: Every significant operation records timestamp, request ID, module, model, agent, hardware, input hash, output hash, decision, authorization, failure → reproducibility and forensic analysis

Execution modes:
MODE 0 AIR-GAPPED
MODE 1 LOCAL ONLY
MODE 2 LOCAL + LAN
MODE 3 LOCAL + APPROVED CLOUD
MODE 4 DISTRIBUTED HYBRID
Policy controls whether network access is permitted
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import time
import hashlib
import uuid

class ExecutionMode(Enum):
    AIR_GAPPED = 0
    LOCAL_ONLY = 1
    LOCAL_LAN = 2
    LOCAL_APPROVED_CLOUD = 3
    DISTRIBUTED_HYBRID = 4

@dataclass
class AuditRecord:
    timestamp: int = field(default_factory=lambda: int(time.time()))
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    module: str = ""
    model: str = ""
    agent: str = ""
    hardware: str = ""
    input_hash: str = ""
    output_hash: str = ""
    decision: str = ""
    authorization: str = ""
    failure: Optional[str] = None

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "request_id": self.request_id,
            "module": self.module,
            "model": self.model,
            "agent": self.agent,
            "hardware": self.hardware,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "decision": self.decision,
            "authorization": self.authorization,
            "failure": self.failure,
        }

class SecurityFabric:
    def __init__(self):
        self.audit_log: List[AuditRecord] = []
        self.execution_mode: ExecutionMode = ExecutionMode.LOCAL_ONLY
        self.capabilities: Dict[str, List[str]] = {}

    def set_execution_mode(self, mode: ExecutionMode):
        self.execution_mode = mode
        print(f"Execution mode set to {mode.name} ({mode.value}): {self.describe_mode(mode)}")

    def describe_mode(self, mode: ExecutionMode) -> str:
        descriptions = {
            ExecutionMode.AIR_GAPPED: "No network, fully offline",
            ExecutionMode.LOCAL_ONLY: "Local machine only",
            ExecutionMode.LOCAL_LAN: "Local + LAN",
            ExecutionMode.LOCAL_APPROVED_CLOUD: "Local + approved cloud",
            ExecutionMode.DISTRIBUTED_HYBRID: "Distributed hybrid",
        }
        return descriptions.get(mode, "Unknown")

    def authenticate(self, module: str, token: str) -> bool:
        # Mock authentication
        return len(token) > 5

    def authorize(self, module: str, resource: str) -> bool:
        # Check capability
        caps = self.capabilities.get(module, [])
        return resource in caps or "all" in caps

    def grant_capability(self, module: str, capability: str):
        if module not in self.capabilities:
            self.capabilities[module] = []
        self.capabilities[module].append(capability)
        print(f"Granted capability {capability} to {module}")

    def audit(self, record: AuditRecord):
        self.audit_log.append(record)
        print(f"Audit: {record.module} {record.decision} auth={record.authorization} input_hash={record.input_hash[:8]} output_hash={record.output_hash[:8]}")

    def check_network_policy(self, destination: str) -> bool:
        # Policy controls whether network access is permitted
        if self.execution_mode == ExecutionMode.AIR_GAPPED:
            return False
        if self.execution_mode == ExecutionMode.LOCAL_ONLY:
            return False
        if self.execution_mode == ExecutionMode.LOCAL_LAN:
            return destination.startswith("lan://") or destination.startswith("local://")
        if self.execution_mode == ExecutionMode.LOCAL_APPROVED_CLOUD:
            return destination in ["approved_cloud://api", "lan://", "local://"]
        if self.execution_mode == ExecutionMode.DISTRIBUTED_HYBRID:
            return True
        return False

class LocalModelRegistry:
    """
    Every installed model has: model ID, architecture, parameters, quantization, modalities, capabilities, hardware requirements, license, evaluation score, safety status, version, hash
    RAJARAM can then select models automatically
    """
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = {}

    def register(self, model_info: Dict[str, Any]):
        model_id = model_info["model_id"]
        self.models[model_id] = model_info
        print(f"Registered model {model_id}: {model_info['architecture']} {model_info['parameters']/1e9:.1f}B")

    def list_models(self) -> List[Dict[str, Any]]:
        return list(self.models.values())

    def select_model(self, task: str, hardware: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # RAJARAM selects models automatically based on task and hardware
        for model_id, info in self.models.items():
            if task.lower() in str(info.get("capabilities",[])).lower() or task.lower() in info.get("modalities",""):
                # Check hardware requirements
                if info.get("memory_required_mb", 0) <= hardware.get("memory_mb", 16384):
                    print(f"Selected model {model_id} for task '{task}' on {hardware}")
                    return info
        # Fallback
        if self.models:
            return list(self.models.values())[0]
        return None

if __name__ == "__main__":
    sec = SecurityFabric()
    for mode in ExecutionMode:
        sec.set_execution_mode(mode)
        print(f"  Network check lan://model: {sec.check_network_policy('lan://model')}, https://api: {sec.check_network_policy('https://api')}")

    sec.grant_capability("SARAM", "CPU")
    sec.grant_capability("SARAM", "GPU")
    sec.grant_capability("RAJARAM", "all")

    print(f"Auth SARAM CPU: {sec.authorize('SARAM','CPU')}")
    print(f"Auth SARAM PLC: {sec.authorize('SARAM','PLC')}")

    # Audit
    record = AuditRecord(
        module="SARAM",
        model="physics_autoencoder",
        agent="PhysicsAgent",
        hardware="NPU-1",
        input_hash=hashlib.sha256(b"vibration 8.3").hexdigest(),
        output_hash=hashlib.sha256(b"fault 0.82").hexdigest(),
        decision="verified",
        authorization="token-123",
    )
    sec.audit(record)

    # Model registry
    print("\n=== Local Model Registry ===")
    registry = LocalModelRegistry()
    registry.register({
        "model_id": "model-7b",
        "architecture": "transformer",
        "parameters": 7_000_000_000,
        "quantization": "int8",
        "modalities": "text,code,physics",
        "capabilities": ["coding","reasoning","physics","EEE"],
        "hardware_requirements": "GPU 8GB",
        "memory_required_mb": 8192,
        "license": "apache-2.0",
        "evaluation_score": 0.85,
        "safety_status": "safe",
        "version": "v0.6.0",
        "hash": "abc123",
    })
    registry.register({
        "model_id": "model-1b-edge",
        "architecture": "transformer",
        "parameters": 1_000_000_000,
        "quantization": "int4",
        "modalities": "text",
        "capabilities": ["general"],
        "hardware_requirements": "CPU",
        "memory_required_mb": 1024,
        "license": "mit",
        "evaluation_score": 0.65,
        "safety_status": "safe",
        "version": "v0.6.0",
        "hash": "def456",
    })

    selected = registry.select_model("bearing fault detection coding", {"memory_mb": 16384})
    print(f"Selected: {selected}")
