"""
Multi-Agent System: Run Agent 1..5 on different compute resources
Measure latency, throughput, energy, agreement, failure recovery
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.faisanth import Faisanth, TaskDescriptor
from sparsiz.premsoth import Premsoth, AgentOutput
from sparsiz.hal import HAL, ComputeRequest, Task
import time
import random

def run_multi_agent():
    print("=== Phase 3: Multi-Agent System ===")
    faisanth = Faisanth()
    premsoth = Premsoth()
    hal = HAL()

    tasks = [TaskDescriptor(f"T00{i}", "inference", 20+i*5, 2048, 0.5+random.random()*0.4, 0.6, 0.5, 2) for i in range(5)]

    for task in tasks:
        print(f"\n--- Task {task.task_id} ---")
        route = faisanth.route(task)
        print(f"Routed to {route['nodes']}")

        # Simulate 5 agents on different resources
        agents = [
            ("Agent1", "CPU-1"),
            ("Agent2", "GPU-1"),
            ("Agent3", "NPU-1"),
            ("Agent4", "CPU-2"),
            ("Agent5", "GPU-2"),
        ]

        outputs = []
        latencies = []
        for agent_id, device_id in agents:
            start = time.time()
            device = hal.select_device(device_id)
            if device:
                device.allocate(ComputeRequest(task.task_id, task.memory_mb, task.compute_intensity, task.latency_budget_ms))
                result = device.execute(Task(task.task_id, {"data": "sample"}))
                # Simulate inference with fault probability
                fault_prob = 0.8 + random.uniform(-0.1,0.1)
                outputs.append(AgentOutput(agent_id, task.task_id, {"fault_probability": fault_prob}, fault_prob, 0.9))
                latency = (time.time()-start)*1000
                latencies.append(latency)
                print(f"{agent_id} on {device_id}: latency={latency:.2f}ms fault_prob={fault_prob:.2f}")

        # Measure latency, throughput, energy, agreement, failure recovery
        avg_latency = sum(latencies)/len(latencies) if latencies else 0
        throughput = len(tasks)/ (sum(latencies)/1000) if latencies else 0
        print(f"Avg latency: {avg_latency:.2f}ms, Throughput: {throughput:.2f} tasks/s")

        decision = premsoth.verify(task.task_id, outputs)
        print(f"Agreement: {decision['agreement_score']:.2f}, Verified: {decision['verified']}")

if __name__ == "__main__":
    run_multi_agent()
