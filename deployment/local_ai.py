"""
LOCAL AI — System must work without Internet

LOCAL MACHINE
  ├── Models, Memory, Tools → RAJARAM LOCAL

Five execution modes:
MODE 0 AIR-GAPPED
MODE 1 LOCAL ONLY
MODE 2 LOCAL + LAN
MODE 3 LOCAL + APPROVED CLOUD
MODE 4 DISTRIBUTED HYBRID

Model Router: USER TASK → TASK CLASSIFIER → MODEL ROUTER → FAISANTH → HARDWARE
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class ExecutionMode(Enum):
    AIR_GAPPED = 0
    LOCAL_ONLY = 1
    LOCAL_LAN = 2
    LOCAL_APPROVED_CLOUD = 3
    DISTRIBUTED_HYBRID = 4

class TaskType(Enum):
    CODING = "coding"
    MATHEMATICS = "mathematics"
    ENGINEERING = "engineering"
    VISION = "vision"
    AUDIO = "audio"
    RESEARCH = "research"
    ROBOTICS = "robotics"
    GENERAL = "general"

class TaskClassifier:
    def classify(self, task: str) -> TaskType:
        task_lower = task.lower()
        if "code" in task_lower or "def " in task_lower:
            return TaskType.CODING
        if "math" in task_lower or "P=VI" in task_lower or "derive" in task_lower:
            return TaskType.MATHEMATICS
        if "vibration" in task_lower or "motor" in task_lower or "EEE" in task_lower:
            return TaskType.ENGINEERING
        if "image" in task_lower or "vision" in task_lower:
            return TaskType.VISION
        if "audio" in task_lower:
            return TaskType.AUDIO
        if "research" in task_lower or "paper" in task_lower:
            return TaskType.RESEARCH
        if "robot" in task_lower:
            return TaskType.ROBOTICS
        return TaskType.GENERAL

class ModelRouter:
    def __init__(self):
        self.models = {
            TaskType.CODING: ["code-7b", "code-14b-moe"],
            TaskType.MATHEMATICS: ["math-7b", "reasoning-14b"],
            TaskType.ENGINEERING: ["physics-7b", "eee-7b"],
            TaskType.VISION: ["vit-300m", "multimodal-7b"],
            TaskType.AUDIO: ["audio-1b"],
            TaskType.RESEARCH: ["research-7b", "multimodal-7b"],
            TaskType.ROBOTICS: ["robotics-3b", "world-model-3b"],
            TaskType.GENERAL: ["general-7b"],
        }

    def route(self, task_type: TaskType, hardware: Dict[str, Any]) -> str:
        candidates = self.models.get(task_type, ["general-7b"])
        # Select based on hardware
        if hardware.get("memory_mb", 4096) < 2048:
            return candidates[-1]  # smallest
        return candidates[0]

class LocalAI:
    def __init__(self):
        self.mode = ExecutionMode.LOCAL_ONLY
        self.classifier = TaskClassifier()
        self.router = ModelRouter()

    def set_mode(self, mode: ExecutionMode):
        self.mode = mode
        print(f"Local AI mode: {mode.name} - {self.describe_mode(mode)}")

    def describe_mode(self, mode: ExecutionMode) -> str:
        return {
            ExecutionMode.AIR_GAPPED: "No network, fully offline, models/memory/tools local",
            ExecutionMode.LOCAL_ONLY: "Local machine only",
            ExecutionMode.LOCAL_LAN: "Local + LAN",
            ExecutionMode.LOCAL_APPROVED_CLOUD: "Local + approved cloud",
            ExecutionMode.DISTRIBUTED_HYBRID: "Distributed hybrid",
        }[mode]

    def execute(self, task: str, hardware: Dict[str, Any]) -> Dict[str, Any]:
        # USER TASK → TASK CLASSIFIER → MODEL ROUTER → FAISANTH → HARDWARE
        task_type = self.classifier.classify(task)
        print(f"Task classifier: '{task}' → {task_type.value}")

        model = self.router.route(task_type, hardware)
        print(f"Model router: {task_type.value} → {model}")

        # FAISANTH routing
        faisanth_hardware = "NPU-1" if hardware.get("latency_budget_ms",100) < 20 else "GPU-1" if hardware.get("memory_mb",4096) > 8000 else "CPU-1"
        print(f"FAISANTH: {model} → {faisanth_hardware} (HARDWARE)")

        return {
            "task": task,
            "task_type": task_type.value,
            "model": model,
            "hardware": faisanth_hardware,
            "mode": self.mode.name,
            "offline": self.mode in [ExecutionMode.AIR_GAPPED, ExecutionMode.LOCAL_ONLY],
        }

if __name__ == "__main__":
    local_ai = LocalAI()

    for mode in ExecutionMode:
        local_ai.set_mode(mode)
        result = local_ai.execute("Bearing fault detection vibration 8.3 mm/s", {"memory_mb": 4096, "latency_budget_ms": 10})
        print(f"Result: {result}\n")

    # Test different tasks
    tasks = [
        "Write Python code for Y-Bus matrix",
        "Derive P=VI and S=P+jQ",
        "Analyze motor vibration 8.3 mm/s",
        "Describe image of motor",
        "Plan robot path",
    ]
    local_ai.set_mode(ExecutionMode.LOCAL_ONLY)
    for task in tasks:
        result = local_ai.execute(task, {"memory_mb": 8192, "latency_budget_ms": 50})
        print(f"Task '{task}' → {result['task_type']} → {result['model']} → {result['hardware']}")
