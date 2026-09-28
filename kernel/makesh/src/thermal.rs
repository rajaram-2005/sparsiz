/*!
 * Thermal monitoring T_i(t)
 */

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThermalState {
    pub devices: HashMap<String, f64>,
    pub max_temp: f64,
    pub avg_temp: f64,
    pub timestamp: u64,
}

#[derive(Debug)]
pub struct ThermalMonitor {
    state: ThermalState,
}

impl ThermalMonitor {
    pub fn new() -> Self {
        Self {
            state: ThermalState {
                devices: HashMap::new(),
                max_temp: 0.0,
                avg_temp: 0.0,
                timestamp: 0,
            },
        }
    }

    pub fn start(&mut self) -> anyhow::Result<()> {
        tracing::info!("Thermal monitor starting");
        self.state.devices.insert("CPU-0".into(), 65.0);
        self.state.devices.insert("GPU-0".into(), 75.0);
        self.state.devices.insert("NPU-0".into(), 55.0);
        self.update_stats();
        Ok(())
    }

    fn update_stats(&mut self) {
        if !self.state.devices.is_empty() {
            self.state.max_temp = self.state.devices.values().cloned().fold(0.0, f64::max);
            self.state.avg_temp = self.state.devices.values().sum::<f64>() / self.state.devices.len() as f64;
        }
    }

    pub fn check_threshold(&self, t_max: f64) -> Vec<String> {
        self.state.devices.iter()
            .filter(|(_, &temp)| temp > t_max)
            .map(|(name, _)| name.clone())
            .collect()
    }

    pub fn current(&self) -> ThermalState {
        self.state.clone()
    }
}

impl Default for ThermalMonitor {
    fn default() -> Self {
        Self::new()
    }
}
