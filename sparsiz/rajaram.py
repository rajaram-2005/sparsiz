"""
RAJARAM CORE Python wrapper — mirrors Rust implementation
Global State S(t)=[C(t),M(t),G(t),T(t),N(t),A(t),H(t)]
Permission Matrix Ω∈{0,1}^{M×R}
Security: Secure Boot→TPM→Identity→Authorization→Execution Token
Master Clock τ(t)
State Machine: BOOT→SELF_TEST→INITIALIZE→READY→INGEST→ROUTE→EXECUTE→VERIFY→AUTHORIZE→COMMIT→IDLE + FAULT path
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time
import uuid
import hashlib

@dataclass
class CpuState:
    utilization: float = 0.0
    frequency_mhz: float = 0.0
    temperature_c: float = 0.0
    load_avg: float = 0.0
    context_switches: int = 0
    cache_miss_rate: float = 0.0
    cores_available: int = 0
    cores_total: int = 0

@dataclass
class MemoryState:
    ram_used_mb: int = 0
    ram_total_mb: int = 0
    swap_used_mb: int = 0
    page_faults: int = 0
    numa_locality: float = 0.0
    bandwidth_gbps: float = 0.0

@dataclass
class GpuState:
    utilization: float = 0.0
    memory_used_mb: int = 0
    memory_total_mb: int = 0
    temperature_c: float = 0.0
    power_w: float = 0.0
    queue_utilization: float = 0.0

@dataclass
class ThermalState:
    devices: Dict[str, float] = field(default_factory=dict)
    max_temp_c: float = 0.0
    avg_temp_c: float = 0.0

@dataclass
class NetworkState:
    latency_ms: float = 0.0
    packet_rate: float = 0.0
    bandwidth_mbps: float = 0.0
    errors: int = 0

@dataclass
class AgentState:
    active_agents: int = 0
    total_tasks: int = 0
    failed_tasks: int = 0
    avg_latency_ms: float = 0.0

@dataclass
class HealthState:
    healthy: bool = True
    fault_count: int = 0

@dataclass
class GlobalState:
    cpu: CpuState = field(default_factory=CpuState)
    memory: MemoryState = field(default_factory=MemoryState)
    gpu: GpuState = field(default_factory=GpuState)
    thermal: ThermalState = field(default_factory=ThermalState)
    network: NetworkState = field(default_factory=NetworkState)
    agent: AgentState = field(default_factory=AgentState)
    health: HealthState = field(default_factory=HealthState)
    timestamp: int = 0

    def as_vector(self):
        # S(t) vector
        return [
            self.cpu.utilization,
            self.memory.ram_used_mb / max(self.memory.ram_total_mb,1),
            self.gpu.utilization,
            self.thermal.max_temp_c / 100.0,
            self.network.latency_ms / 100.0,
            self.agent.active_agents / 10.0,
            1.0 if self.health.healthy else 0.0,
        ]

from enum import Enum

class SystemState(Enum):
    BOOT = "BOOT"
    SELF_TEST = "SELF_TEST"
    INITIALIZE = "INITIALIZE"
    READY = "READY"
    INGEST = "INGEST"
    ROUTE = "ROUTE"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    AUTHORIZE = "AUTHORIZE"
    COMMIT = "COMMIT"
    IDLE = "IDLE"
    FAULT = "FAULT"
    ISOLATE = "ISOLATE"
    DIAGNOSE = "DIAGNOSE"
    QUARANTINE = "QUARANTINE"
    TERMINATE = "TERMINATE"

class StateMachine:
    def __init__(self):
        self.current = SystemState.BOOT
        self.history = [SystemState.BOOT]
        self.valid_transitions = {
            SystemState.BOOT: [SystemState.SELF_TEST],
            SystemState.SELF_TEST: [SystemState.INITIALIZE],
            SystemState.INITIALIZE: [SystemState.READY],
            SystemState.READY: [SystemState.INGEST, SystemState.READY],
            SystemState.INGEST: [SystemState.ROUTE],
            SystemState.ROUTE: [SystemState.EXECUTE],
            SystemState.EXECUTE: [SystemState.VERIFY],
            SystemState.VERIFY: [SystemState.AUTHORIZE, SystemState.QUARANTINE],
            SystemState.AUTHORIZE: [SystemState.COMMIT],
            SystemState.COMMIT: [SystemState.IDLE],
            SystemState.IDLE: [SystemState.INGEST, SystemState.READY, SystemState.IDLE],
            SystemState.FAULT: [SystemState.ISOLATE],
            SystemState.ISOLATE: [SystemState.DIAGNOSE],
            SystemState.DIAGNOSE: [SystemState.READY, SystemState.TERMINATE],
            SystemState.QUARANTINE: [SystemState.DIAGNOSE],
        }

    def transition(self, to: SystemState):
        # FAULT can happen from ANY STATE
        if to == SystemState.FAULT:
            print(f"State transition: {self.current} → {to} (FAULT from any)")
            self.current = to
            self.history.append(to)
            return
        if to in self.valid_transitions.get(self.current, []) or to == self.current:
            print(f"State transition: {self.current} → {to}")
            self.current = to
            self.history.append(to)
        else:
            raise ValueError(f"Invalid transition {self.current} → {to}")

    def is_ready(self):
        return self.current in [SystemState.READY, SystemState.IDLE]

class PermissionMatrix:
    """
    Ω∈{0,1}^{M×R} policy, not crypto
    """
    def __init__(self):
        self.matrix = {}
        self._default_policy()

    def _default_policy(self):
        self.set("SARAM", "CPU", True)
        self.set("SARAM", "GPU", True)
        self.set("SARAM", "BCI", True)
        self.set("SARAM", "PLC", False)
        self.set("SARAM", "Actuator", False)

        self.set("MAKESH", "CPU", True)
        self.set("MAKESH", "GPU", True)
        self.set("MAKESH", "BCI", False)

        self.set("FAISANTH", "CPU", True)
        self.set("FAISANTH", "GPU", True)

        self.set("PREMSOTH", "CPU", True)
        self.set("PREMSOTH", "GPU", True)
        self.set("PREMSOTH", "Actuator", True)

        for res in ["CPU","GPU","NPU","FPGA","BCI","PLC","Actuator","Memory","Network","Storage"]:
            self.set("RAJARAM", res, True)

    def set(self, module: str, resource: str, allowed: bool):
        if module not in self.matrix:
            self.matrix[module] = {}
        self.matrix[module][resource] = allowed

    def is_authorized(self, module: str, resource: str) -> bool:
        return self.matrix.get(module, {}).get(resource, False)

    def as_table(self) -> str:
        s = "Module\\Resource | CPU | GPU | BCI | PLC | Actuator\n"
        s += "----------------|-----|-----|-----|-----|--------\n"
        for mod, res in self.matrix.items():
            s += f"{mod:15} | {int(res.get('CPU',False))}   | {int(res.get('GPU',False))}   | {int(res.get('BCI',False))}   | {int(res.get('PLC',False))}   | {int(res.get('Actuator',False))}\n"
        return s

@dataclass
class MasterClock:
    start: float = field(default_factory=time.time)
    sequence: int = 0

    def now(self) -> int:
        return int((time.time() - self.start) * 1000)

    def uptime(self) -> int:
        return int(time.time() - self.start)

    def create_event(self, module: str, event_type: str, payload: str):
        self.sequence += 1
        h = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return {
            "timestamp": self.now(),
            "module": module,
            "sequence": self.sequence,
            "event": event_type,
            "hash": h,
        }

class RajaramCore:
    def __init__(self, config: Optional[Dict] = None):
        self.id = str(uuid.uuid4())
        self.clock = MasterClock()
        self.state = GlobalState()
        self.state_machine = StateMachine()
        self.permission_matrix = PermissionMatrix()
        self.config = config or {"system": {"name": "the-last-dance", "mode": "research"}}
        self.modules = {}
        self.faults = []

    def initialize(self):
        print(f"RAJARAM CORE initializing id={self.id}")
        self.state_machine.transition(SystemState.SELF_TEST)
        self.state_machine.transition(SystemState.INITIALIZE)
        for mod in ["MAKESH","SARAM","FAISANTH","PREMSOTH"]:
            self.modules[mod] = {"state": "Loaded", "path": mod.lower()}
            print(f"Module loaded: {mod}")
        self.state_machine.transition(SystemState.READY)
        print("RAJARAM CORE READY")

    def execute_pipeline(self, task: Dict) -> Dict:
        start = self.clock.now()
        self.state_machine.transition(SystemState.INGEST)
        ingest = self.clock.create_event("RAJARAM", "TaskIngested", task.get("task_id",""))

        self.state_machine.transition(SystemState.ROUTE)
        route = self.clock.create_event("FAISANTH", "RouteSelected", task.get("task_id",""))

        self.state_machine.transition(SystemState.EXECUTE)
        exec_ev = self.clock.create_event("AGENT", "ExecutionStarted", task.get("task_id",""))

        self.state_machine.transition(SystemState.VERIFY)
        verify = self.clock.create_event("PREMSOTH", "VerificationStarted", task.get("task_id",""))

        self.state_machine.transition(SystemState.AUTHORIZE)
        module = task.get("module","SARAM")
        resource = task.get("resource","CPU")
        if not self.permission_matrix.is_authorized(module, resource):
            self.faults.append({"module": module, "resource": resource, "type": "unauthorized"})
            raise PermissionError(f"Module {module} not authorized for {resource}")

        token = str(uuid.uuid4())

        self.state_machine.transition(SystemState.COMMIT)
        result = {
            "task_id": task.get("task_id"),
            "authorized": True,
            "token": token,
            "latency_ms": self.clock.now() - start,
            "events": [ingest, route, exec_ev, verify],
        }
        self.state_machine.transition(SystemState.IDLE)
        return result

    def health_check(self):
        return {
            "core_id": self.id,
            "state": self.state_machine.current.value,
            "modules": list(self.modules.keys()),
            "faults": self.faults,
            "uptime": self.clock.uptime(),
        }

def main():
    core = RajaramCore()
    core.initialize()
    task = {"task_id": "T001", "module": "SARAM", "resource": "CPU", "type": "inference", "latency_budget_ms": 20, "memory_mb": 4096}
    result = core.execute_pipeline(task)
    print(result)
    print(core.health_check())

if __name__ == "__main__":
    main()
