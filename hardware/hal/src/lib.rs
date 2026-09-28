/*!
 * Hardware Abstraction Layer
 * Common interface:
 * trait ComputeDevice {
 *   fn initialize(&mut self);
 *   fn capabilities(&self) -> Capabilities;
 *   fn allocate(&mut self, request: ComputeRequest);
 *   fn execute(&mut self, task: Task);
 *   fn release(&mut self);
 *   fn telemetry(&self) -> Telemetry;
 * }
 * Implement: CPUDevice, GPUDevice, NPUDevice, FPGADevice, NeuromorphicDevice, QuantumDevice
 * Initially CPUDevice, GPUDevice are enough.
 */

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Capabilities {
    pub device_type: String,
    pub compute_units: u32,
    pub memory_mb: u64,
    pub supports_fp16: bool,
    pub supports_int8: bool,
    pub supports_snn: bool,
    pub supports_qubo: bool,
    pub max_power_w: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComputeRequest {
    pub task_id: String,
    pub memory_mb: u64,
    pub compute_intensity: f64,
    pub latency_budget_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub task_id: String,
    pub payload: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Telemetry {
    pub device_id: String,
    pub utilization: f64,
    pub temperature_c: f64,
    pub power_w: f64,
    pub memory_used_mb: u64,
}

pub trait ComputeDevice: Send + Sync {
    fn initialize(&mut self) -> anyhow::Result<()>;
    fn capabilities(&self) -> Capabilities;
    fn allocate(&mut self, request: ComputeRequest) -> anyhow::Result<()>;
    fn execute(&mut self, task: Task) -> anyhow::Result<serde_json::Value>;
    fn release(&mut self) -> anyhow::Result<()>;
    fn telemetry(&self) -> Telemetry;
    fn device_id(&self) -> String;
}

/// CPU Device
#[derive(Debug)]
pub struct CPUDevice {
    id: String,
    cores: u32,
    memory_mb: u64,
    utilization: f64,
}

impl CPUDevice {
    pub fn new(id: String, cores: u32, memory_mb: u64) -> Self {
        Self { id, cores, memory_mb, utilization: 0.0 }
    }
}

impl ComputeDevice for CPUDevice {
    fn initialize(&mut self) -> anyhow::Result<()> {
        tracing::info!("Initializing CPU device {}", self.id);
        Ok(())
    }

    fn capabilities(&self) -> Capabilities {
        Capabilities {
            device_type: "CPU".into(),
            compute_units: self.cores,
            memory_mb: self.memory_mb,
            supports_fp16: true,
            supports_int8: true,
            supports_snn: false,
            supports_qubo: false,
            max_power_w: 125.0,
        }
    }

    fn allocate(&mut self, request: ComputeRequest) -> anyhow::Result<()> {
        tracing::info!("CPU {} allocating for task {}", self.id, request.task_id);
        self.utilization = 0.5;
        Ok(())
    }

    fn execute(&mut self, task: Task) -> anyhow::Result<serde_json::Value> {
        tracing::info!("CPU {} executing task {}", self.id, task.task_id);
        Ok(serde_json::json!({"device": self.id, "task_id": task.task_id, "result": "cpu_result"}))
    }

    fn release(&mut self) -> anyhow::Result<()> {
        self.utilization = 0.0;
        Ok(())
    }

    fn telemetry(&self) -> Telemetry {
        Telemetry {
            device_id: self.id.clone(),
            utilization: self.utilization,
            temperature_c: 65.0,
            power_w: 65.0,
            memory_used_mb: 1024,
        }
    }

    fn device_id(&self) -> String {
        self.id.clone()
    }
}

/// GPU Device
#[derive(Debug)]
pub struct GPUDevice {
    id: String,
    memory_mb: u64,
    utilization: f64,
}

impl GPUDevice {
    pub fn new(id: String, memory_mb: u64) -> Self {
        Self { id, memory_mb, utilization: 0.0 }
    }
}

impl ComputeDevice for GPUDevice {
    fn initialize(&mut self) -> anyhow::Result<()> {
        tracing::info!("Initializing GPU device {}", self.id);
        Ok(())
    }

    fn capabilities(&self) -> Capabilities {
        Capabilities {
            device_type: "GPU".into(),
            compute_units: 2048,
            memory_mb: self.memory_mb,
            supports_fp16: true,
            supports_int8: true,
            supports_snn: false,
            supports_qubo: false,
            max_power_w: 300.0,
        }
    }

    fn allocate(&mut self, request: ComputeRequest) -> anyhow::Result<()> {
        tracing::info!("GPU {} allocating for task {}", self.id, request.task_id);
        self.utilization = 0.8;
        Ok(())
    }

    fn execute(&mut self, task: Task) -> anyhow::Result<serde_json::Value> {
        tracing::info!("GPU {} executing task {}", self.id, task.task_id);
        Ok(serde_json::json!({"device": self.id, "task_id": task.task_id, "result": "gpu_result"}))
    }

    fn release(&mut self) -> anyhow::Result<()> {
        self.utilization = 0.0;
        Ok(())
    }

    fn telemetry(&self) -> Telemetry {
        Telemetry {
            device_id: self.id.clone(),
            utilization: self.utilization,
            temperature_c: 75.0,
            power_w: 150.0,
            memory_used_mb: 2048,
        }
    }

    fn device_id(&self) -> String {
        self.id.clone()
    }
}

/// NPU Device stub
#[derive(Debug)]
pub struct NPUDevice {
    id: String,
}

impl NPUDevice {
    pub fn new(id: String) -> Self { Self { id } }
}

impl ComputeDevice for NPUDevice {
    fn initialize(&mut self) -> anyhow::Result<()> { tracing::info!("Initializing NPU {}", self.id); Ok(()) }
    fn capabilities(&self) -> Capabilities {
        Capabilities { device_type: "NPU".into(), compute_units: 1, memory_mb: 4096, supports_fp16: true, supports_int8: true, supports_snn: false, supports_qubo: false, max_power_w: 15.0 }
    }
    fn allocate(&mut self, _request: ComputeRequest) -> anyhow::Result<()> { Ok(()) }
    fn execute(&mut self, task: Task) -> anyhow::Result<serde_json::Value> {
        Ok(serde_json::json!({"device": self.id, "task_id": task.task_id, "result": "npu_low_power_inference", "latency_ms": 4}))
    }
    fn release(&mut self) -> anyhow::Result<()> { Ok(()) }
    fn telemetry(&self) -> Telemetry {
        Telemetry { device_id: self.id.clone(), utilization: 0.3, temperature_c: 55.0, power_w: 10.0, memory_used_mb: 512 }
    }
    fn device_id(&self) -> String { self.id.clone() }
}

/// FPGA Device stub
#[derive(Debug)]
pub struct FPGADevice {
    id: String,
}

impl FPGADevice {
    pub fn new(id: String) -> Self { Self { id } }
}

impl ComputeDevice for FPGADevice {
    fn initialize(&mut self) -> anyhow::Result<()> { tracing::info!("Initializing FPGA {}", self.id); Ok(()) }
    fn capabilities(&self) -> Capabilities {
        Capabilities { device_type: "FPGA".into(), compute_units: 1, memory_mb: 2048, supports_fp16: false, supports_int8: true, supports_snn: false, supports_qubo: false, max_power_w: 50.0 }
    }
    fn allocate(&mut self, _request: ComputeRequest) -> anyhow::Result<()> { Ok(()) }
    fn execute(&mut self, task: Task) -> anyhow::Result<serde_json::Value> {
        Ok(serde_json::json!({"device": self.id, "task_id": task.task_id, "result": "fpga_custom_logic"}))
    }
    fn release(&mut self) -> anyhow::Result<()> { Ok(()) }
    fn telemetry(&self) -> Telemetry {
        Telemetry { device_id: self.id.clone(), utilization: 0.4, temperature_c: 60.0, power_w: 30.0, memory_used_mb: 256 }
    }
    fn device_id(&self) -> String { self.id.clone() }
}

/// Neuromorphic Device stub — workloads: event detection, SNN, low-power anomaly detection, temporal pattern recognition
#[derive(Debug)]
pub struct NeuromorphicDevice {
    id: String,
}

impl NeuromorphicDevice {
    pub fn new(id: String) -> Self { Self { id } }
}

impl ComputeDevice for NeuromorphicDevice {
    fn initialize(&mut self) -> anyhow::Result<()> { tracing::info!("Initializing Neuromorphic {}", self.id); Ok(()) }
    fn capabilities(&self) -> Capabilities {
        Capabilities { device_type: "Neuromorphic".into(), compute_units: 1, memory_mb: 512, supports_fp16: false, supports_int8: false, supports_snn: true, supports_qubo: false, max_power_w: 1.0 }
    }
    fn allocate(&mut self, _request: ComputeRequest) -> anyhow::Result<()> { Ok(()) }
    fn execute(&mut self, task: Task) -> anyhow::Result<serde_json::Value> {
        // Flow: Event stream → SNN representation → Neuromorphic accelerator → Event classification → PREMSOTH
        Ok(serde_json::json!({"device": self.id, "task_id": task.task_id, "result": "snn_event_classification", "power_mw": 10}))
    }
    fn release(&mut self) -> anyhow::Result<()> { Ok(()) }
    fn telemetry(&self) -> Telemetry {
        Telemetry { device_id: self.id.clone(), utilization: 0.2, temperature_c: 40.0, power_w: 0.5, memory_used_mb: 64 }
    }
    fn device_id(&self) -> String { self.id.clone() }
}

/// Quantum Device stub — optional external accelerator, not assumed inside system
/// Task classifier → Is problem quantum-suitable? NO→CPU/GPU, YES→Quantum backend
/// Research targets: combinatorial optimization, QUBO, scheduling, sampling, quantum chemistry
#[derive(Debug)]
pub struct QuantumDevice {
    id: String,
}

impl QuantumDevice {
    pub fn new(id: String) -> Self { Self { id } }
}

impl ComputeDevice for QuantumDevice {
    fn initialize(&mut self) -> anyhow::Result<()> { tracing::info!("Initializing Quantum {} (external accelerator)", self.id); Ok(()) }
    fn capabilities(&self) -> Capabilities {
        Capabilities { device_type: "Quantum".into(), compute_units: 1, memory_mb: 0, supports_fp16: false, supports_int8: false, supports_snn: false, supports_qubo: true, max_power_w: 1000.0 }
    }
    fn allocate(&mut self, _request: ComputeRequest) -> anyhow::Result<()> { Ok(()) }
    fn execute(&mut self, task: Task) -> anyhow::Result<serde_json::Value> {
        Ok(serde_json::json!({"device": self.id, "task_id": task.task_id, "result": "quantum_optimization", "note": "QUBO formulation, only when problem formulation and backend justify"}))
    }
    fn release(&mut self) -> anyhow::Result<()> { Ok(()) }
    fn telemetry(&self) -> Telemetry {
        Telemetry { device_id: self.id.clone(), utilization: 0.1, temperature_c: 0, power_w: 500.0, memory_used_mb: 0 }
    }
    fn device_id(&self) -> String { self.id.clone() }
}

/// Device registry
pub struct DeviceRegistry {
    devices: Vec<Box<dyn ComputeDevice>>,
}

impl DeviceRegistry {
    pub fn new() -> Self {
        Self { devices: Vec::new() }
    }

    pub fn register(&mut self, device: Box<dyn ComputeDevice>) {
        self.devices.push(device);
    }

    pub fn default_registry() -> Self {
        let mut reg = Self::new();
        reg.register(Box::new(CPUDevice::new("CPU-1".into(), 8, 16384)));
        reg.register(Box::new(CPUDevice::new("CPU-2".into(), 8, 16384)));
        reg.register(Box::new(GPUDevice::new("GPU-1".into(), 8192)));
        reg.register(Box::new(GPUDevice::new("GPU-2".into(), 8192)));
        reg.register(Box::new(NPUDevice::new("NPU-1".into())));
        reg.register(Box::new(NPUDevice::new("NPU-2".into())));
        reg.register(Box::new(FPGADevice::new("FPGA-1".into())));
        reg.register(Box::new(NeuromorphicDevice::new("NEURO-1".into())));
        reg.register(Box::new(QuantumDevice::new("QUANTUM-1".into())));
        reg
    }

    pub fn list_telemetry(&self) -> Vec<Telemetry> {
        self.devices.iter().map(|d| d.telemetry()).collect()
    }

    pub fn find_best_for_task(&self, request: &ComputeRequest) -> Option<String> {
        // Simplified: select based on latency budget, memory, etc.
        // In real FAISANTH integration, use cost function
        if request.memory_mb > 8000 {
            Some("GPU-1".into())
        } else if request.compute_intensity > 0.8 {
            Some("NPU-1".into())
        } else {
            Some("CPU-1".into())
        }
    }
}

impl Default for DeviceRegistry {
    fn default() -> Self {
        Self::default_registry()
    }
}
