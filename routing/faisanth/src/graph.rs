/*!
 * Compute Graph G=(V,E)
 * V={v1..vn} compute nodes
 * Node: capacity/latency/memory/thermal/energy/reliability/specialization
 * Edge: bandwidth/latency/energy/reliability
 */

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum NodeCapabilities {
    Cpu,
    Gpu,
    Npu,
    Fpga,
    Neuromorphic,
    Quantum,
    Edge,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComputeNode {
    pub id: String,
    pub capabilities: Vec<NodeCapabilities>,
    pub capacity: f64,
    pub latency_ms: f64,
    pub memory_mb: u64,
    pub thermal_c: f64,
    pub energy_cost: f64,
    pub reliability: f64, // 0..1, higher better
    pub specialization: f64,
    pub available: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComputeEdge {
    pub from: String,
    pub to: String,
    pub bandwidth_gbps: f64,
    pub latency_ms: f64,
    pub energy_cost: f64,
    pub reliability: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComputeGraph {
    pub nodes: HashMap<String, ComputeNode>,
    pub edges: Vec<ComputeEdge>,
}

impl ComputeGraph {
    pub fn new() -> Self {
        Self {
            nodes: HashMap::new(),
            edges: Vec::new(),
        }
    }

    /// 10 simulated nodes per spec Phase 2: CPU-1/2, GPU-1/2, NPU-1/2, FPGA-1, EDGE-1/2/3
    pub fn default_10_nodes() -> Self {
        let mut graph = Self::new();
        
        let nodes = vec![
            ComputeNode { id: "CPU-1".into(), capabilities: vec![NodeCapabilities::Cpu], capacity: 1.0, latency_ms: 14.0, memory_mb: 16384, thermal_c: 60.0, energy_cost: 0.2, reliability: 0.95, specialization: 0.5, available: true },
            ComputeNode { id: "CPU-2".into(), capabilities: vec![NodeCapabilities::Cpu], capacity: 1.0, latency_ms: 15.0, memory_mb: 16384, thermal_c: 65.0, energy_cost: 0.25, reliability: 0.94, specialization: 0.5, available: true },
            ComputeNode { id: "GPU-1".into(), capabilities: vec![NodeCapabilities::Gpu], capacity: 5.0, latency_ms: 7.0, memory_mb: 8192, thermal_c: 75.0, energy_cost: 0.7, reliability: 0.92, specialization: 0.9, available: true },
            ComputeNode { id: "GPU-2".into(), capabilities: vec![NodeCapabilities::Gpu], capacity: 5.0, latency_ms: 8.0, memory_mb: 8192, thermal_c: 78.0, energy_cost: 0.75, reliability: 0.91, specialization: 0.9, available: true },
            ComputeNode { id: "NPU-1".into(), capabilities: vec![NodeCapabilities::Npu], capacity: 3.0, latency_ms: 4.0, memory_mb: 4096, thermal_c: 55.0, energy_cost: 0.1, reliability: 0.88, specialization: 0.95, available: true },
            ComputeNode { id: "NPU-2".into(), capabilities: vec![NodeCapabilities::Npu], capacity: 3.0, latency_ms: 4.5, memory_mb: 4096, thermal_c: 58.0, energy_cost: 0.12, reliability: 0.87, specialization: 0.95, available: true },
            ComputeNode { id: "FPGA-1".into(), capabilities: vec![NodeCapabilities::Fpga], capacity: 2.0, latency_ms: 6.0, memory_mb: 2048, thermal_c: 60.0, energy_cost: 0.3, reliability: 0.85, specialization: 0.8, available: true },
            ComputeNode { id: "EDGE-1".into(), capabilities: vec![NodeCapabilities::Edge], capacity: 0.5, latency_ms: 20.0, memory_mb: 1024, thermal_c: 45.0, energy_cost: 0.05, reliability: 0.7, specialization: 0.3, available: true },
            ComputeNode { id: "EDGE-2".into(), capabilities: vec![NodeCapabilities::Edge], capacity: 0.5, latency_ms: 22.0, memory_mb: 1024, thermal_c: 47.0, energy_cost: 0.06, reliability: 0.68, specialization: 0.3, available: true },
            ComputeNode { id: "EDGE-3".into(), capabilities: vec![NodeCapabilities::Edge], capacity: 0.5, latency_ms: 25.0, memory_mb: 1024, thermal_c: 50.0, energy_cost: 0.07, reliability: 0.65, specialization: 0.3, available: true },
        ];

        for node in nodes {
            graph.nodes.insert(node.id.clone(), node);
        }

        // Create mesh-like edges: CPU-1 / \ CPU-2, GPU-1---CPU-2, NPU---GPU-2 etc per spec
        graph.edges.push(ComputeEdge { from: "CPU-1".into(), to: "CPU-2".into(), bandwidth_gbps: 25.6, latency_ms: 1.0, energy_cost: 0.1, reliability: 0.99 });
        graph.edges.push(ComputeEdge { from: "CPU-1".into(), to: "GPU-1".into(), bandwidth_gbps: 16.0, latency_ms: 2.0, energy_cost: 0.2, reliability: 0.98 });
        graph.edges.push(ComputeEdge { from: "GPU-1".into(), to: "CPU-2".into(), bandwidth_gbps: 16.0, latency_ms: 2.0, energy_cost: 0.2, reliability: 0.98 });
        graph.edges.push(ComputeEdge { from: "GPU-1".into(), to: "NPU-1".into(), bandwidth_gbps: 8.0, latency_ms: 3.0, energy_cost: 0.15, reliability: 0.95 });
        graph.edges.push(ComputeEdge { from: "NPU-1".into(), to: "GPU-2".into(), bandwidth_gbps: 8.0, latency_ms: 3.0, energy_cost: 0.15, reliability: 0.95 });
        graph.edges.push(ComputeEdge { from: "CPU-2".into(), to: "GPU-2".into(), bandwidth_gbps: 16.0, latency_ms: 2.0, energy_cost: 0.2, reliability: 0.98 });
        graph.edges.push(ComputeEdge { from: "GPU-2".into(), to: "FPGA-1".into(), bandwidth_gbps: 4.0, latency_ms: 5.0, energy_cost: 0.25, reliability: 0.9 });
        graph.edges.push(ComputeEdge { from: "FPGA-1".into(), to: "EDGE-1".into(), bandwidth_gbps: 1.0, latency_ms: 10.0, energy_cost: 0.1, reliability: 0.8 });
        graph.edges.push(ComputeEdge { from: "EDGE-1".into(), to: "EDGE-2".into(), bandwidth_gbps: 0.5, latency_ms: 15.0, energy_cost: 0.05, reliability: 0.7 });
        graph.edges.push(ComputeEdge { from: "EDGE-2".into(), to: "EDGE-3".into(), bandwidth_gbps: 0.5, latency_ms: 15.0, energy_cost: 0.05, reliability: 0.7 });

        graph
    }

    pub fn get_node(&self, id: &str) -> Option<&ComputeNode> {
        self.nodes.get(id)
    }

    pub fn neighbors(&self, id: &str) -> Vec<&ComputeEdge> {
        self.edges.iter().filter(|e| e.from == id || e.to == id).collect()
    }
}

impl Default for ComputeGraph {
    fn default() -> Self {
        Self::default_10_nodes()
    }
}
