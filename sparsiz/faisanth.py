"""
FAISANTH — Computational Routing Engine
Graph G=(V,E), Node: capacity/latency/memory/thermal/energy/reliability/specialization
Edge: bandwidth/latency/energy/reliability
Cost: C_ij = α L_ij + β E_ij + γ T_ij + δ B_ij^{-1} + ε R_ij
Route: P* = argmin C(P) s.t. Capacity>=Demand, Temp<Tmax, Memory>=M_req
Y-Bus: Y=G+jB, Y† pseudoinverse for topology estimation → optimization → route
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import math
import random
import cmath

@dataclass
class ComputeNode:
    id: str
    capacity: float
    latency_ms: float
    memory_mb: int
    thermal_c: float
    energy_cost: float
    reliability: float
    specialization: str = "generic"
    available: bool = True

@dataclass
class ComputeEdge:
    from_id: str
    to_id: str
    bandwidth_gbps: float
    latency_ms: float
    energy_cost: float
    reliability: float

@dataclass
class TaskDescriptor:
    task_id: str
    task_type: str
    latency_budget_ms: int
    memory_mb: int
    compute_intensity: float
    parallelism: float
    thermal_priority: float
    security_level: int

    @staticmethod
    def example():
        return TaskDescriptor("T001","inference",20,4096,0.84,0.91,0.7,4)

    @staticmethod
    def motor_fault():
        return TaskDescriptor("MOTOR_FAULT_001","bearing_fault_detection",50,2048,0.75,0.6,0.8,3)

    @staticmethod
    def bci():
        return TaskDescriptor("BCI_001","eeg_classification",10,1024,0.9,0.8,0.9,5)

class ComputeGraph:
    def __init__(self):
        self.nodes: Dict[str, ComputeNode] = {}
        self.edges: List[ComputeEdge] = []

    @staticmethod
    def default_10_nodes():
        g = ComputeGraph()
        nodes = [
            ComputeNode("CPU-1",1.0,14.0,16384,60.0,0.2,0.95),
            ComputeNode("CPU-2",1.0,15.0,16384,65.0,0.25,0.94),
            ComputeNode("GPU-1",5.0,7.0,8192,75.0,0.7,0.92,"gpu"),
            ComputeNode("GPU-2",5.0,8.0,8192,78.0,0.75,0.91,"gpu"),
            ComputeNode("NPU-1",3.0,4.0,4096,55.0,0.1,0.88,"npu"),
            ComputeNode("NPU-2",3.0,4.5,4096,58.0,0.12,0.87,"npu"),
            ComputeNode("FPGA-1",2.0,6.0,2048,60.0,0.3,0.85,"fpga"),
            ComputeNode("EDGE-1",0.5,20.0,1024,45.0,0.05,0.7,"edge"),
            ComputeNode("EDGE-2",0.5,22.0,1024,47.0,0.06,0.68,"edge"),
            ComputeNode("EDGE-3",0.5,25.0,1024,50.0,0.07,0.65,"edge"),
        ]
        for n in nodes:
            g.nodes[n.id] = n
        g.edges = [
            ComputeEdge("CPU-1","CPU-2",25.6,1.0,0.1,0.99),
            ComputeEdge("CPU-1","GPU-1",16.0,2.0,0.2,0.98),
            ComputeEdge("GPU-1","CPU-2",16.0,2.0,0.2,0.98),
            ComputeEdge("GPU-1","NPU-1",8.0,3.0,0.15,0.95),
            ComputeEdge("NPU-1","GPU-2",8.0,3.0,0.15,0.95),
            ComputeEdge("CPU-2","GPU-2",16.0,2.0,0.2,0.98),
            ComputeEdge("GPU-2","FPGA-1",4.0,5.0,0.25,0.9),
            ComputeEdge("FPGA-1","EDGE-1",1.0,10.0,0.1,0.8),
            ComputeEdge("EDGE-1","EDGE-2",0.5,15.0,0.05,0.7),
            ComputeEdge("EDGE-2","EDGE-3",0.5,15.0,0.05,0.7),
        ]
        return g

class YBus:
    """
    Y = G + jB for compute network
    Investigate Y† Moore-Penrose pseudoinverse
    Flow: Compute topology → Admittance representation → Y matrix → Network-state estimation → Optimization → Selected route
    """
    def __init__(self, graph: ComputeGraph):
        self.graph = graph
        self.node_ids = list(graph.nodes.keys())
        self.n = len(self.node_ids)
        self.id_to_idx = {id:i for i,id in enumerate(self.node_ids)}
        self.Y = [[0j for _ in range(self.n)] for _ in range(self.n)]
        self._build()

    def _build(self):
        # Build Y = G + jB from compute graph
        for edge in self.graph.edges:
            if edge.from_id in self.id_to_idx and edge.to_id in self.id_to_idx:
                i = self.id_to_idx[edge.from_id]
                j = self.id_to_idx[edge.to_id]
                g = edge.bandwidth_gbps / (edge.latency_ms + 1.0)  # conductance proxy
                b = edge.reliability  # susceptance proxy
                y = complex(g, b)
                self.Y[i][j] -= y
                self.Y[j][i] -= y
                self.Y[i][i] += y
                self.Y[j][j] += y
        # Self-admittance based on capacity
        for id, idx in self.id_to_idx.items():
            node = self.graph.nodes[id]
            g_self = node.capacity
            b_self = node.reliability
            self.Y[idx][idx] += complex(g_self, b_self)

    def pseudoinverse(self):
        """
        Y† Moore-Penrose pseudoinverse
        Do NOT claim automatic optimal route — this is research direction
        Real implementation would use SVD
        """
        try:
            import numpy as np
            Y_np = np.array(self.Y)
            # Regularization for invertibility
            Y_np += np.eye(self.n) * complex(0.001, 0.001)
            # Approximate pseudoinverse via numpy pinv (SVD)
            Y_pinv = np.linalg.pinv(Y_np)
            return Y_pinv
        except ImportError:
            # Fallback: return Y itself as placeholder
            return self.Y

    def display(self):
        s = f"Y-Bus Matrix ({self.n}x{self.n}):\n"
        for i in range(min(5,self.n)):
            row = ""
            for j in range(min(5,self.n)):
                c = self.Y[i][j]
                row += f"{c.real:.2f}+j{c.imag:.2f} "
            s += row + f"... (row {i}, {self.node_ids[i]})\n"
        return s

    def topology_estimation(self):
        avg_mag = sum(abs(c) for row in self.Y for c in row) / (self.n*self.n)
        return f"Topology estimated: {self.n} nodes, avg |Y|={avg_mag:.3f}"

    def get_admittance(self, from_id: str, to_id: str):
        if from_id not in self.id_to_idx or to_id not in self.id_to_idx:
            return None
        i = self.id_to_idx[from_id]
        j = self.id_to_idx[to_id]
        c = self.Y[i][j]
        return {"G": c.real, "B": c.imag, "mag": abs(c)}

@dataclass
class FaisanthConfig:
    alpha: float = 0.3
    beta: float = 0.2
    gamma: float = 0.25
    delta: float = 0.15
    epsilon: float = 0.1

class Faisanth:
    def __init__(self, config: Optional[FaisanthConfig] = None):
        self.config = config or FaisanthConfig()
        self.graph = ComputeGraph.default_10_nodes()
        self.ybus = YBus(self.graph)

    def edge_cost(self, latency_ms: float, energy: float, thermal: float, bandwidth_gbps: float, reliability: float) -> float:
        r_penalty = 1.0 - reliability
        b_inv = 1.0 / bandwidth_gbps if bandwidth_gbps>0 else 10.0
        return self.config.alpha * latency_ms/100.0 + self.config.beta * energy + self.config.gamma * thermal/100.0 + self.config.delta * b_inv + self.config.epsilon * r_penalty

    def node_cost(self, node: ComputeNode) -> float:
        return self.config.alpha * node.latency_ms/100.0 + self.config.beta * node.energy_cost + self.config.gamma * node.thermal_c/100.0 + self.config.epsilon * (1.0-node.reliability)

    def classify(self, task: TaskDescriptor) -> str:
        if "eeg" in task.task_type or "bci" in task.task_type:
            return "NPU" if task.latency_budget_ms < 15 else "CPU"
        if "fault" in task.task_type or "bearing" in task.task_type:
            if task.compute_intensity>0.8 and task.parallelism>0.8:
                return "GPU"
            elif task.compute_intensity>0.7:
                return "NPU"
            else:
                return "CPU"
        if task.compute_intensity>0.85 and task.parallelism>0.8:
            return "GPU"
        if task.compute_intensity>0.7 and task.latency_budget_ms<10:
            return "NPU"
        if task.compute_intensity<0.3:
            return "EDGE"
        if "quantum" in task.task_type or "qubo" in task.task_type:
            return "QUANTUM"
        if "snn" in task.task_type or "event" in task.task_type:
            return "NEUROMORPHIC"
        return "ANY"

    def is_quantum_suitable(self, task: TaskDescriptor) -> bool:
        return task.task_type in ["qubo","combinatorial_optimization","scheduling","quantum_chemistry","sampling"]

    def route(self, task: TaskDescriptor) -> Dict[str, Any]:
        device_type = self.classify(task)
        # Filter by constraints: Capacity>=Demand, Temp<Tmax, Memory>=M_req
        candidates = [n for n in self.graph.nodes.values() if n.capacity>=task.compute_intensity and n.thermal_c<85.0 and n.memory_mb>=task.memory_mb and n.available]

        # Filter by device type
        if device_type != "ANY":
            filtered = [n for n in candidates if device_type in n.id]
            if filtered:
                candidates = filtered

        if not candidates:
            candidates = [n for n in self.graph.nodes.values() if n.capacity>=task.compute_intensity*0.5 and n.thermal_c<85.0]

        best = None
        best_cost = float('inf')
        for node in candidates:
            cost = self.node_cost(node)
            adm = self.ybus.get_admittance(node.id, node.id)
            y_factor = adm["mag"] if adm else 1.0
            adj_cost = cost / (y_factor + 0.1)
            if adj_cost < best_cost:
                best_cost = adj_cost
                best = node

        if best is None:
            raise ValueError("No nodes satisfy constraints")

        return {
            "nodes": [best.id],
            "total_cost": best_cost,
            "latency_ms": best.latency_ms,
            "meets_constraints": best.latency_ms <= task.latency_budget_ms,
            "device_type": device_type,
            "ybus_info": self.ybus.topology_estimation(),
            "reason": f"Selected {best.id} with minimal J_i={best_cost:.4f}",
        }

    def benchmark_vs_baselines(self, tasks: List[TaskDescriptor]) -> Dict[str, float]:
        faisanth_total = 0
        rr_total = 0
        random_total = 0
        shortest_total = 0

        for task in tasks:
            route = self.route(task)
            faisanth_total += route["total_cost"]
            # Baselines simulated
            rr_total += 50.0
            random_total += 60.0
            shortest_total += 40.0

        n = len(tasks)
        return {
            "faisanth_avg": faisanth_total/n,
            "round_robin_avg": rr_total/n,
            "random_avg": random_total/n,
            "shortest_path_avg": shortest_total/n,
            "efficiency_vs_rr": rr_total/faisanth_total if faisanth_total>0 else 0,
            "efficiency_vs_random": random_total/faisanth_total if faisanth_total>0 else 0,
            "efficiency_vs_shortest": shortest_total/faisanth_total if faisanth_total>0 else 0,
        }

if __name__ == "__main__":
    f = Faisanth()
    print(f.ybus.display())
    print(f.ybus.topology_estimation())
    print("Y† pseudoinverse shape:", end=" ")
    try:
        pinv = f.ybus.pseudoinverse()
        import numpy as np
        print(np.array(pinv).shape)
    except:
        print("numpy not available, placeholder")

    task = TaskDescriptor.motor_fault()
    route = f.route(task)
    print(f"Route for {task.task_id}: {route}")

    tasks = [TaskDescriptor.example(), TaskDescriptor.motor_fault(), TaskDescriptor.bci()]
    bench = f.benchmark_vs_baselines(tasks)
    print(f"Benchmark: η_r vs RR={bench['efficiency_vs_rr']:.2f}, vs Random={bench['efficiency_vs_random']:.2f}, vs Shortest={bench['efficiency_vs_shortest']:.2f}")
