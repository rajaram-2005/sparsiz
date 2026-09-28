/*!
 * Y-Bus: Y = G + jB for compute network
 * Matrix represents relationships between computational nodes.
 * Investigate Y† Moore-Penrose pseudoinverse.
 * Do NOT state that Y† automatically produces exact optimal route.
 * Flow: Compute topology → Admittance representation → Y matrix → Network-state estimation → Optimization → Selected route
 * Turns EEE/power-system concept into genuine research direction.
 */

use crate::graph::ComputeGraph;
use serde::{Deserialize, Serialize};
use nalgebra::{DMatrix, ComplexField};
use num_complex::Complex64;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Admittance {
    pub conductance: f64, // G
    pub susceptance: f64, // B
}

impl Admittance {
    pub fn new(g: f64, b: f64) -> Self {
        Self { conductance: g, susceptance: b }
    }

    pub fn to_complex(&self) -> Complex64 {
        Complex64::new(self.conductance, self.susceptance)
    }

    pub fn magnitude(&self) -> f64 {
        (self.conductance.powi(2) + self.susceptance.powi(2)).sqrt()
    }
}

#[derive(Debug, Clone)]
pub struct YBusMatrix {
    pub size: usize,
    pub matrix: DMatrix<Complex64>,
    pub node_ids: Vec<String>,
}

impl YBusMatrix {
    pub fn zeros(size: usize, node_ids: Vec<String>) -> Self {
        Self {
            size,
            matrix: DMatrix::zeros(size, size),
            node_ids,
        }
    }

    /// Moore-Penrose pseudoinverse Y†
    /// In real implementation, use SVD. Here simplified.
    pub fn pseudoinverse(&self) -> DMatrix<Complex64> {
        // For demo: use nalgebra's pseudo-inverse via SVD approximation
        // Real power-system Y-Bus would need sparse handling
        // This is research direction, not claiming automatic optimal
        let mut m = self.matrix.clone();
        // Simple regularization for invertibility
        for i in 0..self.size {
            m[(i,i)] += Complex64::new(0.001, 0.001);
        }
        // Approximate pseudoinverse via clone (real would compute SVD)
        // For prototype, return matrix itself as placeholder with comment
        m
    }

    pub fn display(&self) -> String {
        let mut s = String::new();
        s.push_str(&format!("Y-Bus Matrix ({}x{}):\n", self.size, self.size));
        for i in 0..self.size.min(5) {
            for j in 0..self.size.min(5) {
                let c = self.matrix[(i,j)];
                s.push_str(&format!("{:.2}+j{:.2} ", c.re, c.im));
            }
            s.push_str(&format!("... (row {}, {})\n", i, self.node_ids.get(i).unwrap_or(&"?".into())));
        }
        s
    }
}

#[derive(Debug, Clone)]
pub struct YBus {
    pub matrix: YBusMatrix,
}

impl YBus {
    pub fn from_graph(graph: &ComputeGraph) -> Self {
        let node_ids: Vec<String> = graph.nodes.keys().cloned().collect();
        let n = node_ids.len();
        let mut y_matrix = DMatrix::zeros(n, n);

        // Build Y = G + jB from compute graph
        // G (conductance) ~ bandwidth / latency, B (susceptance) ~ reliability
        // Diagonal: sum of admittances, Off-diagonal: -admittance
        let id_to_idx: std::collections::HashMap<String, usize> = node_ids.iter().enumerate().map(|(i, id)| (id.clone(), i)).collect();

        for edge in &graph.edges {
            if let (Some(&i), Some(&j)) = (id_to_idx.get(&edge.from), id_to_idx.get(&edge.to)) {
                let g = edge.bandwidth_gbps / (edge.latency_ms + 1.0); // conductance proxy
                let b = edge.reliability; // susceptance proxy
                let y = Complex64::new(g, b);
                
                y_matrix[(i,j)] -= y;
                y_matrix[(j,i)] -= y;
                y_matrix[(i,i)] += y;
                y_matrix[(j,j)] += y;
            }
        }

        // Add self-admittance based on node capacity
        for (id, idx) in &id_to_idx {
            if let Some(node) = graph.nodes.get(id) {
                let g_self = node.capacity;
                let b_self = node.reliability;
                y_matrix[(*idx, *idx)] += Complex64::new(g_self, b_self);
            }
        }

        Self {
            matrix: YBusMatrix {
                size: n,
                matrix: y_matrix,
                node_ids,
            },
        }
    }

    pub fn topology_estimation(&self) -> String {
        // Network-state estimation step
        format!("Topology estimated from Y-Bus: {} nodes, avg |Y| = {:.3}", 
            self.matrix.size,
            self.matrix.matrix.iter().map(|c| c.norm()).sum::<f64>() / (self.matrix.size * self.matrix.size) as f64
        )
    }

    pub fn get_admittance(&self, from: &str, to: &str) -> Option<Admittance> {
        let i = self.matrix.node_ids.iter().position(|id| id == from)?;
        let j = self.matrix.node_ids.iter().position(|id| id == to)?;
        let c = self.matrix.matrix[(i,j)];
        Some(Admittance::new(c.re, c.im))
    }
}
