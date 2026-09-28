/*!
 * Permission Matrix Ω∈{0,1}^{M×R}
 * M modules, R resources
 * Policy, not cryptography. Real security via OS perms, capabilities, IOMMU, TPM, etc.
 */

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Resource {
    Cpu,
    Gpu,
    Npu,
    Fpga,
    Neuromorphic,
    Quantum,
    Bci,
    Plc,
    Actuator,
    Memory,
    Network,
    Storage,
}

impl std::fmt::Display for Resource {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:?}", self)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourcePolicy {
    pub resource: Resource,
    pub max_access: u32,
    pub requires_auth: bool,
    pub security_level: u8,
}

#[derive(Debug, Clone)]
pub struct PermissionMatrix {
    /// Ω matrix: module -> resource -> bool
    matrix: HashMap<String, HashMap<Resource, bool>>,
}

impl PermissionMatrix {
    pub fn new() -> Self {
        Self {
            matrix: HashMap::new(),
        }
    }

    /// Default policy per spec example
    pub fn default_policy() -> Self {
        let mut pm = Self::new();
        // SARAM: CPU,GPU,BCI allowed
        pm.set("SARAM", Resource::Cpu, true);
        pm.set("SARAM", Resource::Gpu, true);
        pm.set("SARAM", Resource::Bci, true);
        pm.set("SARAM", Resource::Plc, false);
        pm.set("SARAM", Resource::Actuator, false);

        // MAKESH: CPU,GPU
        pm.set("MAKESH", Resource::Cpu, true);
        pm.set("MAKESH", Resource::Gpu, true);
        pm.set("MAKESH", Resource::Bci, false);
        pm.set("MAKESH", Resource::Plc, false);
        pm.set("MAKESH", Resource::Actuator, false);

        // FAISANTH: CPU,GPU
        pm.set("FAISANTH", Resource::Cpu, true);
        pm.set("FAISANTH", Resource::Gpu, true);
        pm.set("FAISANTH", Resource::Bci, false);
        pm.set("FAISANTH", Resource::Plc, false);
        pm.set("FAISANTH", Resource::Actuator, false);

        // PREMSOTH: CPU,GPU,Actuator (via safety gate)
        pm.set("PREMSOTH", Resource::Cpu, true);
        pm.set("PREMSOTH", Resource::Gpu, true);
        pm.set("PREMSOTH", Resource::Bci, false);
        pm.set("PREMSOTH", Resource::Plc, false);
        pm.set("PREMSOTH", Resource::Actuator, true);

        // RAJARAM: all
        for res in [
            Resource::Cpu,
            Resource::Gpu,
            Resource::Npu,
            Resource::Fpga,
            Resource::Bci,
            Resource::Plc,
            Resource::Actuator,
            Resource::Memory,
            Resource::Network,
            Resource::Storage,
        ] {
            pm.set("RAJARAM", res, true);
        }

        pm
    }

    pub fn set(&mut self, module: &str, resource: Resource, allowed: bool) {
        self.matrix
            .entry(module.to_string())
            .or_default()
            .insert(resource, allowed);
    }

    pub fn is_authorized(&self, module: &str, resource: &Resource) -> bool {
        self.matrix
            .get(module)
            .and_then(|m| m.get(resource))
            .copied()
            .unwrap_or(false)
    }

    pub fn check(&self, module: &str, resource: &Resource) -> Result<(), String> {
        if self.is_authorized(module, resource) {
            Ok(())
        } else {
            Err(format!("Module {} not authorized for resource {}", module, resource))
        }
    }

    pub fn matrix_as_table(&self) -> String {
        let mut s = String::from("Module\\Resource | CPU | GPU | BCI | PLC | Actuator\n");
        s.push_str("----------------|-----|-----|-----|-----|--------\n");
        for (module, resources) in &self.matrix {
            s.push_str(&format!(
                "{:15} | {:3} | {:3} | {:3} | {:3} | {:3}\n",
                module,
                if *resources.get(&Resource::Cpu).unwrap_or(&false) { "1" } else { "0" },
                if *resources.get(&Resource::Gpu).unwrap_or(&false) { "1" } else { "0" },
                if *resources.get(&Resource::Bci).unwrap_or(&false) { "1" } else { "0" },
                if *resources.get(&Resource::Plc).unwrap_or(&false) { "1" } else { "0" },
                if *resources.get(&Resource::Actuator).unwrap_or(&false) { "1" } else { "0" },
            ));
        }
        s
    }
}

impl Default for PermissionMatrix {
    fn default() -> Self {
        Self::default_policy()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_policy() {
        let pm = PermissionMatrix::default_policy();
        assert!(pm.is_authorized("SARAM", &Resource::Cpu));
        assert!(pm.is_authorized("SARAM", &Resource::Bci));
        assert!(!pm.is_authorized("SARAM", &Resource::Plc));
        assert!(!pm.is_authorized("SARAM", &Resource::Actuator));
        assert!(pm.is_authorized("PREMSOTH", &Resource::Actuator));
    }
}
