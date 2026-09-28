/*!
 * FAISANTH Optimizer
 * C_ij = α L_ij + β E_ij + γ T_ij + δ B_ij^{-1} + ε R_ij
 * P* = argmin C(P) s.t. Capacity>=Demand, Temp<Tmax, Memory>=M_req
 */

use crate::graph::{ComputeGraph, ComputeNode};
use crate::ybus::YBus;
use crate::{FaisanthConfig, policies::{TaskDescriptor, DeviceType}};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoutingCost {
    pub edge_cost: f64,
    pub node_cost: f64,
    pub total: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OptimizationConstraints {
    pub demand: f64,
    pub memory_required_mb: u64,
    pub latency_budget_ms: f64,
    pub t_max: f64,
    pub device_type: DeviceType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Route {
    pub nodes: Vec<String>,
    pub total_cost: f64,
    pub latency_ms: f64,
    pub meets_constraints: bool,
    pub ybus_info: String,
}

#[derive(Debug)]
pub struct Optimizer {
    config: FaisanthConfig,
}

impl Optimizer {
    pub fn new(config: FaisanthConfig) -> Self {
        Self { config }
    }

    /// C_ij = α L_ij + β E_ij + γ T_ij + δ B_ij^{-1} + ε R_ij
    pub fn edge_cost(&self, latency_ms: f64, energy: f64, thermal: f64, bandwidth_gbps: f64, reliability: f64) -> f64 {
        let r_penalty = 1.0 - reliability; // R_ij
        let b_inv = if bandwidth_gbps > 0.0 { 1.0 / bandwidth_gbps } else { 10.0 };
        
        self.config.alpha * latency_ms / 100.0
            + self.config.beta * energy
            + self.config.gamma * thermal / 100.0
            + self.config.delta * b_inv
            + self.config.epsilon * r_penalty
    }

    pub fn node_cost(&self, node: &ComputeNode) -> f64 {
        // Similar cost for node selection
        self.config.alpha * node.latency_ms / 100.0
            + self.config.beta * node.energy_cost
            + self.config.gamma * node.thermal_c / 100.0
            + self.config.epsilon * (1.0 - node.reliability)
    }

    /// Find optimal route P* = argmin C(P)
    pub fn find_optimal_route(
        &self,
        graph: &ComputeGraph,
        ybus: &YBus,
        constraints: &OptimizationConstraints,
    ) -> anyhow::Result<Route> {
        // Filter nodes by constraints
        let mut candidates: Vec<&ComputeNode> = graph.nodes.values()
            .filter(|n| n.capacity >= constraints.demand)
            .filter(|n| n.thermal_c < constraints.t_max)
            .filter(|n| n.memory_mb >= constraints.memory_required_mb)
            .filter(|n| n.available)
            .collect();

        // Filter by device type
        candidates.retain(|n| match constraints.device_type {
            DeviceType::Cpu => n.id.contains("CPU"),
            DeviceType::Gpu => n.id.contains("GPU"),
            DeviceType::Npu => n.id.contains("NPU"),
            DeviceType::Fpga => n.id.contains("FPGA"),
            DeviceType::Neuromorphic => n.id.contains("NEURO"),
            DeviceType::Quantum => n.id.contains("QUANTUM"),
            DeviceType::Edge => n.id.contains("EDGE"),
            DeviceType::Any => true,
            DeviceType::Multiple => true,
        });

        if candidates.is_empty() {
            // Fallback to any that meets basic constraints
            candidates = graph.nodes.values()
                .filter(|n| n.capacity >= constraints.demand * 0.5)
                .filter(|n| n.thermal_c < constraints.t_max)
                .collect();
        }

        if candidates.is_empty() {
            anyhow::bail!("No nodes satisfy constraints");
        }

        // Compute cost for each candidate
        let mut best: Option<(&ComputeNode, f64)> = None;
        for node in &candidates {
            let cost = self.node_cost(node);
            // Add Y-Bus influence: nodes with higher admittance centrality preferred
            // This is where Y† pseudoinverse could inform routing (research direction)
            let ybus_factor = ybus.get_admittance(&node.id, &node.id)
                .map(|a| a.magnitude())
                .unwrap_or(1.0);
            let adjusted_cost = cost / (ybus_factor + 0.1);

            if best.is_none() || adjusted_cost < best.unwrap().1 {
                best = Some((node, adjusted_cost));
            }
        }

        let (selected_node, cost) = best.unwrap();

        // Check latency budget
        let meets = selected_node.latency_ms <= constraints.latency_budget_ms;

        Ok(Route {
            nodes: vec![selected_node.id.clone()],
            total_cost: cost,
            latency_ms: selected_node.latency_ms,
            meets_constraints: meets,
            ybus_info: ybus.topology_estimation(),
        })
    }

    /// Dijkstra shortest path using C_ij cost (for multi-hop routing)
    pub fn shortest_path(&self, graph: &ComputeGraph, from: &str, to: &str) -> Option<Route> {
        // Simplified Dijkstra for prototype
        // In production, use proper graph algorithm with C_ij weights
        let from_node = graph.get_node(from)?;
        let to_node = graph.get_node(to)?;

        // For V1, if direct edge exists, use it
        for edge in &graph.edges {
            if (edge.from == from && edge.to == to) || (edge.from == to && edge.to == from) {
                let cost = self.edge_cost(edge.latency_ms, edge.energy_cost, 50.0, edge.bandwidth_gbps, edge.reliability);
                return Some(Route {
                    nodes: vec![from.to_string(), to.to_string()],
                    total_cost: cost + self.node_cost(from_node) + self.node_cost(to_node),
                    latency_ms: edge.latency_ms + from_node.latency_ms + to_node.latency_ms,
                    meets_constraints: true,
                    ybus_info: "direct edge".into(),
                });
            }
        }
        None
    }
}
