/*!
 * MAKESH KERNEL — Hardware observation and resource-management subsystem
 * Should not replace Linux scheduler initially.
 * Flow: Linux Scheduler → eBPF telemetry → MAKESH → Resource policy → CPU affinity/cgroups/GPU selection
 *
 * eBPF programs attach to kernel execution points, collect/influence subject to program type and verifier restrictions.
 * eBPF maps provide kernel/user-space communication.
 *
 * Telemetry: CPU util/freq/temp/load/ctx switches/cache/core availability
 *            GPU util/memory/temp/power/queue
 *            Memory RAM/swap/page faults/NUMA/bandwidth
 *            Network latency/packet rate/bandwidth/errors
 *            Thermal T_i(t)
 *
 * Scheduling Model: J_i = w1 L_i + w2 T_i + w3 E_i + w4 U_i + w5 R_i, i*=argmin J_i
 */

pub mod scheduler;
pub mod telemetry;
pub mod thermal;
pub mod ebpf;

pub use scheduler::{Scheduler, CostWeights, NodeCost, SchedulingDecision};
pub use telemetry::{TelemetryCollector, CpuTelemetry, GpuTelemetry, MemoryTelemetry, NetworkTelemetry, SystemTelemetry};
pub use thermal::{ThermalMonitor, ThermalState};
pub use ebpf::{EbpfManager, EbpfProgramType};

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourcePolicy {
    pub cpu_affinity: Option<Vec<u32>>,
    pub cgroup: Option<String>,
    pub gpu_selection: Option<u32>,
    pub accelerator_selection: Option<String>,
}

#[derive(Debug)]
pub struct Makesh {
    pub telemetry_collector: TelemetryCollector,
    pub scheduler: Scheduler,
    pub thermal_monitor: ThermalMonitor,
    pub ebpf_manager: EbpfManager,
}

impl Makesh {
    pub fn new() -> Self {
        Self {
            telemetry_collector: TelemetryCollector::new(),
            scheduler: Scheduler::new(CostWeights::default()),
            thermal_monitor: ThermalMonitor::new(),
            ebpf_manager: EbpfManager::new(),
        }
    }

    pub async fn initialize(&mut self) -> anyhow::Result<()> {
        tracing::info!("MAKESH initializing");
        self.ebpf_manager.load_programs()?;
        self.telemetry_collector.start().await?;
        self.thermal_monitor.start()?;
        Ok(())
    }

    pub fn get_telemetry(&self) -> SystemTelemetry {
        self.telemetry_collector.current()
    }

    /// Recommend resource based on cost function J_i
    pub fn recommend(&self, task: &TaskRequirements) -> SchedulingDecision {
        self.scheduler.schedule(task)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskRequirements {
    pub task_id: String,
    pub cpu_required: f64,
    pub memory_mb: u64,
    pub gpu_required: bool,
    pub latency_budget_ms: u64,
    pub thermal_priority: f64,
}

impl Default for Makesh {
    fn default() -> Self {
        Self::new()
    }
}
