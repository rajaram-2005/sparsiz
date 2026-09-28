/*!
 * Telemetry collectors: CPU, GPU, Memory, Network, Thermal
 * Collects T_i(t) for every monitored device i
 */

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CpuTelemetry {
    pub utilization: f64, // 0..1
    pub frequency_mhz: f64,
    pub temperature_c: f64,
    pub load_avg: f64,
    pub context_switches: u64,
    pub cache_miss_rate: f64,
    pub cores_available: u32,
    pub cores_total: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct GpuTelemetry {
    pub utilization: f64,
    pub memory_used_mb: u64,
    pub memory_total_mb: u64,
    pub temperature_c: f64,
    pub power_w: f64,
    pub queue_utilization: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct MemoryTelemetry {
    pub ram_used_mb: u64,
    pub ram_total_mb: u64,
    pub swap_used_mb: u64,
    pub page_faults: u64,
    pub numa_locality: f64,
    pub bandwidth_gbps: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkTelemetry {
    pub latency_ms: f64,
    pub packet_rate: f64,
    pub bandwidth_mbps: f64,
    pub errors: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SystemTelemetry {
    pub cpu: CpuTelemetry,
    pub gpu: GpuTelemetry,
    pub memory: MemoryTelemetry,
    pub network: NetworkTelemetry,
    pub thermal: HashMap<String, f64>, // T_i(t)
    pub timestamp: u64,
}

#[derive(Debug)]
pub struct TelemetryCollector {
    current: SystemTelemetry,
}

impl TelemetryCollector {
    pub fn new() -> Self {
        Self {
            current: SystemTelemetry::default(),
        }
    }

    pub async fn start(&mut self) -> anyhow::Result<()> {
        tracing::info!("Telemetry collector starting (eBPF maps, ring buffers, perf buffers)");
        // In V1, simulate reading from /proc, sysfs, nvidia-smi, etc.
        // In production: eBPF programs collect scheduling telemetry, memory, network
        self.refresh();
        Ok(())
    }

    fn refresh(&mut self) {
        // Simulate realistic values
        self.current.cpu = CpuTelemetry {
            utilization: 0.45,
            frequency_mhz: 3200.0,
            temperature_c: 65.0,
            load_avg: 2.5,
            context_switches: 100000,
            cache_miss_rate: 0.05,
            cores_available: 6,
            cores_total: 8,
        };
        self.current.gpu = GpuTelemetry {
            utilization: 0.7,
            memory_used_mb: 4096,
            memory_total_mb: 8192,
            temperature_c: 75.0,
            power_w: 150.0,
            queue_utilization: 0.6,
        };
        self.current.memory = MemoryTelemetry {
            ram_used_mb: 8192,
            ram_total_mb: 16384,
            swap_used_mb: 0,
            page_faults: 1000,
            numa_locality: 0.95,
            bandwidth_gbps: 25.6,
        };
        self.current.network = NetworkTelemetry {
            latency_ms: 5.0,
            packet_rate: 10000.0,
            bandwidth_mbps: 1000.0,
            errors: 0,
        };
        self.current.thermal.insert("CPU".into(), 65.0);
        self.current.thermal.insert("GPU-0".into(), 75.0);
        self.current.thermal.insert("NPU-0".into(), 55.0);
    }

    pub fn current(&self) -> SystemTelemetry {
        self.current.clone()
    }

    /// Benchmark copy vs zero-copy latency (spec section 28)
    pub fn benchmark_copy_vs_zerocopy(&self) -> (f64, f64) {
        // Simulated: copy latency higher
        let copy_latency_us = 120.0;
        let zero_copy_latency_us = 15.0;
        tracing::info!("Copy latency: {}μs, Zero-copy latency: {}μs", copy_latency_us, zero_copy_latency_us);
        (copy_latency_us, zero_copy_latency_us)
    }
}

impl Default for TelemetryCollector {
    fn default() -> Self {
        Self::new()
    }
}
