/*!
 * Configuration
 * Example TOML from spec section 57
 */

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemConfig {
    pub system: SystemSection,
    pub rajaram: RajaramSection,
    pub makesh: MakeshSection,
    pub saram: SaramSection,
    pub faisanth: FaisanthSection,
    pub premsoth: PremsothSection,
    pub hardware: HardwareSection,
}

impl SystemConfig {
    pub fn default_config() -> Self {
        Self {
            system: SystemSection {
                name: "the-last-dance".into(),
                mode: "research".into(),
            },
            rajaram: RajaramSection {
                security_level: "high".into(),
                audit: true,
            },
            makesh: MakeshSection {
                ebpf: true,
                thermal_monitoring: true,
                cpu_affinity: true,
            },
            saram: SaramSection {
                encoder: "physics_autoencoder".into(),
                latent_dimension: 128,
            },
            faisanth: FaisanthSection {
                routing: "adaptive".into(),
                topology: "compute_grid".into(),
                optimization: "constrained".into(),
            },
            premsoth: PremsothSection {
                verification: true,
                minimum_agents: 3,
                safety_gate: true,
            },
            hardware: HardwareSection {
                cpu: true,
                gpu: true,
                npu: false,
                quantum: false,
                neuromorphic: false,
            },
        }
    }

    pub fn from_toml_str(s: &str) -> anyhow::Result<Self> {
        let cfg: Self = toml::from_str(s)?;
        Ok(cfg)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemSection {
    pub name: String,
    pub mode: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RajaramSection {
    pub security_level: String,
    pub audit: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MakeshSection {
    pub ebpf: bool,
    pub thermal_monitoring: bool,
    pub cpu_affinity: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SaramSection {
    pub encoder: String,
    pub latent_dimension: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FaisanthSection {
    pub routing: String,
    pub topology: String,
    pub optimization: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PremsothSection {
    pub verification: bool,
    pub minimum_agents: usize,
    pub safety_gate: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HardwareSection {
    pub cpu: bool,
    pub gpu: bool,
    pub npu: bool,
    pub quantum: bool,
    pub neuromorphic: bool,
}

impl Default for SystemConfig {
    fn default() -> Self {
        Self::default_config()
    }
}
