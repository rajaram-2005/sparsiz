/*!
 * Global State S(t) = [C(t), M(t), G(t), T(t), N(t), A(t), H(t)]
 * C CPU, M memory, G GPU/accel, T thermal, N network, A agent, H health/fault
 */

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GlobalState {
    pub cpu: CpuState,
    pub memory: MemoryState,
    pub gpu: GpuState,
    pub thermal: ThermalState,
    pub network: NetworkState,
    pub agent: AgentState,
    pub health: HealthState,
    pub timestamp: u64,
}

impl GlobalState {
    pub fn new() -> Self {
        Self {
            cpu: CpuState::default(),
            memory: MemoryState::default(),
            gpu: GpuState::default(),
            thermal: ThermalState::default(),
            network: NetworkState::default(),
            agent: AgentState::default(),
            health: HealthState::default(),
            timestamp: 0,
        }
    }

    /// S(t) vector representation for telemetry
    pub fn as_vector(&self) -> Vec<f64> {
        let mut v = Vec::new();
        v.extend(self.cpu.as_vector());
        v.extend(self.memory.as_vector());
        v.extend(self.gpu.as_vector());
        v.extend(self.thermal.as_vector());
        v.extend(self.network.as_vector());
        v.extend(self.agent.as_vector());
        v.extend(self.health.as_vector());
        v
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CpuState {
    pub utilization: f64, // 0..1
    pub frequency_mhz: f64,
    pub temperature_c: f64,
    pub load_avg: f64,
    pub context_switches: u64,
    pub cache_miss_rate: f64,
    pub cores_available: u32,
    pub cores_total: u32,
}

impl CpuState {
    pub fn as_vector(&self) -> Vec<f64> {
        vec![
            self.utilization,
            self.frequency_mhz / 5000.0,
            self.temperature_c / 100.0,
            self.load_avg / 10.0,
            self.cache_miss_rate,
            self.cores_available as f64 / self.cores_total.max(1) as f64,
        ]
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct MemoryState {
    pub ram_used_mb: u64,
    pub ram_total_mb: u64,
    pub swap_used_mb: u64,
    pub page_faults: u64,
    pub numa_locality: f64,
    pub bandwidth_gbps: f64,
}

impl MemoryState {
    pub fn as_vector(&self) -> Vec<f64> {
        vec![
            self.ram_used_mb as f64 / self.ram_total_mb.max(1) as f64,
            self.swap_used_mb as f64 / 1024.0,
            self.numa_locality,
            self.bandwidth_gbps / 100.0,
        ]
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct GpuState {
    pub utilization: f64,
    pub memory_used_mb: u64,
    pub memory_total_mb: u64,
    pub temperature_c: f64,
    pub power_w: f64,
    pub queue_utilization: f64,
    pub count: u32,
}

impl GpuState {
    pub fn as_vector(&self) -> Vec<f64> {
        vec![
            self.utilization,
            self.memory_used_mb as f64 / self.memory_total_mb.max(1) as f64,
            self.temperature_c / 100.0,
            self.power_w / 500.0,
            self.queue_utilization,
        ]
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ThermalState {
    /// T_i(t) for every monitored device i
    pub devices: HashMap<String, f64>,
    pub max_temp_c: f64,
    pub avg_temp_c: f64,
}

impl ThermalState {
    pub fn as_vector(&self) -> Vec<f64> {
        vec![self.max_temp_c / 100.0, self.avg_temp_c / 100.0]
    }

    pub fn update(&mut self, device: String, temp: f64) {
        self.devices.insert(device, temp);
        self.max_temp_c = self.devices.values().cloned().fold(0.0, f64::max);
        self.avg_temp_c = if self.devices.is_empty() {
            0.0
        } else {
            self.devices.values().sum::<f64>() / self.devices.len() as f64
        };
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct NetworkState {
    pub latency_ms: f64,
    pub packet_rate: f64,
    pub bandwidth_mbps: f64,
    pub errors: u64,
}

impl NetworkState {
    pub fn as_vector(&self) -> Vec<f64> {
        vec![
            self.latency_ms / 100.0,
            self.packet_rate / 10000.0,
            self.bandwidth_mbps / 10000.0,
        ]
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AgentState {
    pub active_agents: u32,
    pub total_tasks: u64,
    pub failed_tasks: u64,
    pub avg_latency_ms: f64,
}

impl AgentState {
    pub fn as_vector(&self) -> Vec<f64> {
        vec![
            self.active_agents as f64 / 10.0,
            self.failed_tasks as f64 / self.total_tasks.max(1) as f64,
            self.avg_latency_ms / 1000.0,
        ]
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct HealthState {
    pub healthy: bool,
    pub fault_count: u32,
    pub last_fault_timestamp: Option<u64>,
}

impl HealthState {
    pub fn as_vector(&self) -> Vec<f64> {
        vec![if self.healthy { 1.0 } else { 0.0 }, self.fault_count as f64 / 100.0]
    }
}
