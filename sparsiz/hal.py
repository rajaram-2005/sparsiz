"""
HAL — Hardware Abstraction Layer
trait ComputeDevice { initialize, capabilities, allocate, execute, release, telemetry }
CPUDevice, GPUDevice, NPUDevice, FPGADevice, NeuromorphicDevice, QuantumDevice
Initially CPUDevice, GPUDevice enough
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import abc

@dataclass
class Capabilities:
    device_type: str
    compute_units: int
    memory_mb: int
    supports_fp16: bool
    supports_int8: bool
    supports_snn: bool
    supports_qubo: bool
    max_power_w: float

@dataclass
class ComputeRequest:
    task_id: str
    memory_mb: int
    compute_intensity: float
    latency_budget_ms: int

@dataclass
class Task:
    task_id: str
    payload: Any

@dataclass
class Telemetry:
    device_id: str
    utilization: float
    temperature_c: float
    power_w: float
    memory_used_mb: int

class ComputeDevice(abc.ABC):
    @abc.abstractmethod
    def initialize(self): pass
    @abc.abstractmethod
    def capabilities(self) -> Capabilities: pass
    @abc.abstractmethod
    def allocate(self, request: ComputeRequest): pass
    @abc.abstractmethod
    def execute(self, task: Task) -> Any: pass
    @abc.abstractmethod
    def release(self): pass
    @abc.abstractmethod
    def telemetry(self) -> Telemetry: pass
    @abc.abstractmethod
    def device_id(self) -> str: pass

class CPUDevice(ComputeDevice):
    def __init__(self, id: str, cores: int = 8, memory_mb: int = 16384):
        self.id = id
        self.cores = cores
        self.memory_mb = memory_mb
        self.util = 0.0

    def initialize(self):
        print(f"Initializing CPU {self.id}")

    def capabilities(self) -> Capabilities:
        return Capabilities("CPU", self.cores, self.memory_mb, True, True, False, False, 125.0)

    def allocate(self, request: ComputeRequest):
        self.util = 0.5

    def execute(self, task: Task) -> Any:
        return {"device": self.id, "task_id": task.task_id, "result": "cpu_result"}

    def release(self):
        self.util = 0.0

    def telemetry(self) -> Telemetry:
        return Telemetry(self.id, self.util, 65.0, 65.0, 1024)

    def device_id(self) -> str:
        return self.id

class GPUDevice(ComputeDevice):
    def __init__(self, id: str, memory_mb: int = 8192):
        self.id = id
        self.memory_mb = memory_mb
        self.util = 0.0

    def initialize(self):
        print(f"Initializing GPU {self.id}")

    def capabilities(self) -> Capabilities:
        return Capabilities("GPU", 2048, self.memory_mb, True, True, False, False, 300.0)

    def allocate(self, request: ComputeRequest):
        self.util = 0.8

    def execute(self, task: Task) -> Any:
        return {"device": self.id, "task_id": task.task_id, "result": "gpu_result"}

    def release(self):
        self.util = 0.0

    def telemetry(self) -> Telemetry:
        return Telemetry(self.id, self.util, 75.0, 150.0, 2048)

    def device_id(self) -> str:
        return self.id

class NPUDevice(ComputeDevice):
    def __init__(self, id: str):
        self.id = id

    def initialize(self):
        print(f"Initializing NPU {self.id}")

    def capabilities(self) -> Capabilities:
        return Capabilities("NPU",1,4096,True,True,False,False,15.0)

    def allocate(self, request: ComputeRequest):
        pass

    def execute(self, task: Task) -> Any:
        return {"device": self.id, "task_id": task.task_id, "result": "npu_low_power_inference", "latency_ms":4}

    def release(self):
        pass

    def telemetry(self) -> Telemetry:
        return Telemetry(self.id,0.3,55.0,10.0,512)

    def device_id(self) -> str:
        return self.id

class FPGADevice(ComputeDevice):
    def __init__(self, id: str):
        self.id = id

    def initialize(self):
        print(f"Initializing FPGA {self.id}")

    def capabilities(self) -> Capabilities:
        return Capabilities("FPGA",1,2048,False,True,False,False,50.0)

    def allocate(self, request: ComputeRequest):
        pass

    def execute(self, task: Task) -> Any:
        return {"device": self.id, "task_id": task.task_id, "result": "fpga_custom_logic"}

    def release(self):
        pass

    def telemetry(self) -> Telemetry:
        return Telemetry(self.id,0.4,60.0,30.0,256)

    def device_id(self) -> str:
        return self.id

class NeuromorphicDevice(ComputeDevice):
    def __init__(self, id: str):
        self.id = id

    def initialize(self):
        print(f"Initializing Neuromorphic {self.id}")

    def capabilities(self) -> Capabilities:
        return Capabilities("Neuromorphic",1,512,False,False,True,False,1.0)

    def allocate(self, request: ComputeRequest):
        pass

    def execute(self, task: Task) -> Any:
        # Event stream → SNN representation → Neuromorphic accelerator → Event classification → PREMSOTH
        return {"device": self.id, "task_id": task.task_id, "result": "snn_event_classification", "power_mw":10}

    def release(self):
        pass

    def telemetry(self) -> Telemetry:
        return Telemetry(self.id,0.2,40.0,0.5,64)

    def device_id(self) -> str:
        return self.id

class QuantumDevice(ComputeDevice):
    def __init__(self, id: str):
        self.id = id

    def initialize(self):
        print(f"Initializing Quantum {self.id} (external accelerator)")

    def capabilities(self) -> Capabilities:
        return Capabilities("Quantum",1,0,False,False,False,True,1000.0)

    def allocate(self, request: ComputeRequest):
        pass

    def execute(self, task: Task) -> Any:
        return {"device": self.id, "task_id": task.task_id, "result": "quantum_optimization", "note":"QUBO formulation, only when problem formulation and backend justify"}

    def release(self):
        pass

    def telemetry(self) -> Telemetry:
        return Telemetry(self.id,0.1,0,500.0,0)

    def device_id(self) -> str:
        return self.id

class HAL:
    def __init__(self):
        self.devices: List[ComputeDevice] = []
        self._default_registry()

    def _default_registry(self):
        self.devices = [
            CPUDevice("CPU-1",8,16384),
            CPUDevice("CPU-2",8,16384),
            GPUDevice("GPU-1",8192),
            GPUDevice("GPU-2",8192),
            NPUDevice("NPU-1"),
            NPUDevice("NPU-2"),
            FPGADevice("FPGA-1"),
            NeuromorphicDevice("NEURO-1"),
            QuantumDevice("QUANTUM-1"),
        ]

    def register(self, device: ComputeDevice):
        self.devices.append(device)

    def list_telemetry(self) -> List[Telemetry]:
        return [d.telemetry() for d in self.devices]

    def find_best_for_task(self, request: ComputeRequest) -> Optional[str]:
        if request.memory_mb>8000:
            return "GPU-1"
        elif request.compute_intensity>0.8:
            return "NPU-1"
        else:
            return "CPU-1"

    def select_device(self, device_id: str) -> Optional[ComputeDevice]:
        for d in self.devices:
            if d.device_id()==device_id:
                return d
        return None
