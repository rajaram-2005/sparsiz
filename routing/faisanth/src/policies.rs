/*!
 * FAISANTH Task Classification
 * Every incoming task gets descriptor, then FAISANTH determines CPU? GPU? NPU? FPGA? Neuromorphic? External? Multiple?
 */

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum DeviceType {
    Cpu,
    Gpu,
    Npu,
    Fpga,
    Neuromorphic,
    Quantum,
    Edge,
    Any,
    Multiple,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskDescriptor {
    pub task_id: String,
    pub task_type: String, // inference, training, etc
    pub latency_budget_ms: u64,
    pub memory_mb: u64,
    pub compute_intensity: f64, // 0..1
    pub parallelism: f64,       // 0..1
    pub thermal_priority: f64,  // 0..1
    pub security_level: u8,
}

impl TaskDescriptor {
    pub fn example() -> Self {
        Self {
            task_id: "T001".into(),
            task_type: "inference".into(),
            latency_budget_ms: 20,
            memory_mb: 4096,
            compute_intensity: 0.84,
            parallelism: 0.91,
            thermal_priority: 0.7,
            security_level: 4,
        }
    }

    pub fn motor_fault() -> Self {
        Self {
            task_id: "MOTOR_FAULT_001".into(),
            task_type: "bearing_fault_detection".into(),
            latency_budget_ms: 50,
            memory_mb: 2048,
            compute_intensity: 0.75,
            parallelism: 0.6,
            thermal_priority: 0.8,
            security_level: 3,
        }
    }

    pub fn bci_inference() -> Self {
        Self {
            task_id: "BCI_001".into(),
            task_type: "eeg_classification".into(),
            latency_budget_ms: 10,
            memory_mb: 1024,
            compute_intensity: 0.9,
            parallelism: 0.8,
            thermal_priority: 0.9,
            security_level: 5,
        }
    }
}

#[derive(Debug)]
pub struct TaskClassifier;

impl TaskClassifier {
    pub fn new() -> Self {
        Self
    }

    /// Determine device type based on task descriptor
    /// Logic: What is task? What HW can execute it? Available? latency? thermal? energy? reliability? SELECT
    pub fn classify(&self, task: &TaskDescriptor) -> DeviceType {
        // Simple heuristic per spec
        if task.task_type.contains("eeg") || task.task_type.contains("bci") {
            if task.latency_budget_ms < 15 {
                return DeviceType::Npu; // low latency BCI -> NPU
            } else {
                return DeviceType::Cpu;
            }
        }

        if task.task_type.contains("fault") || task.task_type.contains("bearing") {
            if task.compute_intensity > 0.8 && task.parallelism > 0.8 {
                return DeviceType::Gpu;
            } else if task.compute_intensity > 0.7 {
                return DeviceType::Npu;
            } else {
                return DeviceType::Cpu;
            }
        }

        if task.compute_intensity > 0.85 && task.parallelism > 0.8 {
            return DeviceType::Gpu;
        }

        if task.compute_intensity > 0.7 && task.latency_budget_ms < 10 {
            return DeviceType::Npu;
        }

        if task.compute_intensity < 0.3 {
            return DeviceType::Edge;
        }

        if task.task_type.contains("quantum") || task.task_type.contains("qubo") {
            return DeviceType::Quantum;
        }

        if task.task_type.contains("snn") || task.task_type.contains("event") {
            return DeviceType::Neuromorphic;
        }

        DeviceType::Any
    }

    /// Quantum suitability check: Don't implement NP-hard→Quantum automatically
    /// Instead: Task classifier → Is problem quantum-suitable? NO→CPU/GPU, YES→Quantum backend
    pub fn is_quantum_suitable(&self, task: &TaskDescriptor) -> bool {
        matches!(
            task.task_type.as_str(),
            "qubo" | "combinatorial_optimization" | "scheduling" | "quantum_chemistry" | "sampling"
        )
    }
}

impl Default for TaskClassifier {
    fn default() -> Self {
        Self::new()
    }
}
