"""
OBSERVABILITY

RAJARAM: system state, security, faults
MAKESH: CPU, GPU, memory, thermal
SARAM: input, latency, compression
FAISANTH: routes, costs, resources
PREMSOTH: verification, failures, rejection

Use Prometheus, Grafana, OpenTelemetry, structured logs
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
import time

@dataclass
class Metric:
    name: str
    value: float
    timestamp: int = field(default_factory=lambda: int(time.time()))
    labels: Dict[str, str] = field(default_factory=dict)

class PrometheusMetrics:
    def __init__(self):
        self.metrics: List[Metric] = []

    def record(self, name: str, value: float, labels: Dict[str, str] = None):
        self.metrics.append(Metric(name=name, value=value, labels=labels or {}))

    def get_metrics(self) -> List[Metric]:
        return self.metrics

    def export_prometheus_format(self) -> str:
        lines = []
        for m in self.metrics:
            label_str = ",".join([f'{k}="{v}"' for k,v in m.labels.items()])
            if label_str:
                lines.append(f'{m.name}{{{label_str}}} {m.value} {m.timestamp}')
            else:
                lines.append(f'{m.name} {m.value} {m.timestamp}')
        return "\n".join(lines)

class ObservabilityFabric:
    def __init__(self):
        self.prometheus = PrometheusMetrics()

    def record_rajaram(self, state: str, security_events: int, faults: int):
        self.prometheus.record("rajaram_system_state", 1, {"state": state})
        self.prometheus.record("rajaram_security_events", security_events)
        self.prometheus.record("rajaram_faults", faults)

    def record_makesh(self, cpu_util: float, gpu_util: float, memory_used: float, thermal_max: float):
        self.prometheus.record("makesh_cpu_utilization", cpu_util)
        self.prometheus.record("makesh_gpu_utilization", gpu_util)
        self.prometheus.record("makesh_memory_used_mb", memory_used)
        self.prometheus.record("makesh_thermal_max_c", thermal_max)

    def record_saram(self, input_rate: float, latency_ms: float, compression_ratio: float, reconstruction_error: float):
        self.prometheus.record("saram_input_rate", input_rate)
        self.prometheus.record("saram_latency_ms", latency_ms)
        self.prometheus.record("saram_compression_ratio", compression_ratio)
        self.prometheus.record("saram_reconstruction_error", reconstruction_error)

    def record_faisanth(self, routes: int, cost: float, resource_util: float):
        self.prometheus.record("faisanth_routes", routes)
        self.prometheus.record("faisanth_cost", cost)
        self.prometheus.record("faisanth_resource_utilization", resource_util)

    def record_premsoth(self, verification: int, failures: int, rejection: int):
        self.prometheus.record("premsoth_verification", verification)
        self.prometheus.record("premsoth_failures", failures)
        self.prometheus.record("premsoth_rejection", rejection)

    def structured_log(self, module: str, event: str, data: Dict[str, Any]):
        print(f"[{module}] {event}: {data} (OpenTelemetry structured log)")

if __name__ == "__main__":
    obs = ObservabilityFabric()
    obs.record_rajaram("READY", 0, 0)
    obs.record_makesh(0.45, 0.7, 8192, 75.0)
    obs.record_saram(100, 5.0, 8.0, 0.01)
    obs.record_faisanth(10, 0.02, 0.6)
    obs.record_premsoth(1, 0, 0)
    obs.structured_log("RAJARAM", "TaskIngested", {"task_id": "T001", "latency_ms": 2.0})

    print("\n=== Prometheus Metrics ===")
    print(obs.prometheus.export_prometheus_format())
