/*!
 * Module lifecycle: load/start/pause/resume/stop/restart/quarantine
 */

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use thiserror::Error;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ModuleState {
    Unloaded,
    Loaded,
    Starting,
    Running,
    Paused,
    Stopping,
    Stopped,
    Quarantined,
    Failed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModuleInfo {
    pub name: String,
    pub path: String,
    pub state: ModuleState,
    pub version: String,
    pub loaded_at: u64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum LifecycleAction {
    Load,
    Start,
    Pause,
    Resume,
    Stop,
    Restart,
    Quarantine,
}

#[derive(Debug, Error)]
pub enum LifecycleError {
    #[error("Module {0} not found")]
    NotFound(String),
    #[error("Invalid transition for module {0}: {1:?} -> {2:?}")]
    InvalidTransition(String, ModuleState, ModuleState),
    #[error("Module {0} already exists")]
    AlreadyExists(String),
}

#[derive(Debug, Default)]
pub struct ModuleManager {
    modules: HashMap<String, ModuleInfo>,
}

impl ModuleManager {
    pub fn new() -> Self {
        Self {
            modules: HashMap::new(),
        }
    }

    pub fn load(&mut self, name: String, path: String) -> Result<(), LifecycleError> {
        if self.modules.contains_key(&name) {
            return Err(LifecycleError::AlreadyExists(name));
        }
        let info = ModuleInfo {
            name: name.clone(),
            path,
            state: ModuleState::Loaded,
            version: "0.6.0".into(),
            loaded_at: 0,
        };
        tracing::info!("Module loaded: {}", name);
        self.modules.insert(name, info);
        Ok(())
    }

    pub fn start(&mut self, name: &str) -> Result<(), LifecycleError> {
        let m = self.modules.get_mut(name).ok_or_else(|| LifecycleError::NotFound(name.into()))?;
        match m.state {
            ModuleState::Loaded | ModuleState::Stopped | ModuleState::Paused => {
                m.state = ModuleState::Running;
                tracing::info!("Module started: {}", name);
                Ok(())
            }
            _ => Err(LifecycleError::InvalidTransition(name.into(), m.state, ModuleState::Running)),
        }
    }

    pub fn pause(&mut self, name: &str) -> Result<(), LifecycleError> {
        let m = self.modules.get_mut(name).ok_or_else(|| LifecycleError::NotFound(name.into()))?;
        if m.state == ModuleState::Running {
            m.state = ModuleState::Paused;
            Ok(())
        } else {
            Err(LifecycleError::InvalidTransition(name.into(), m.state, ModuleState::Paused))
        }
    }

    pub fn resume(&mut self, name: &str) -> Result<(), LifecycleError> {
        let m = self.modules.get_mut(name).ok_or_else(|| LifecycleError::NotFound(name.into()))?;
        if m.state == ModuleState::Paused {
            m.state = ModuleState::Running;
            Ok(())
        } else {
            Err(LifecycleError::InvalidTransition(name.into(), m.state, ModuleState::Running))
        }
    }

    pub fn stop(&mut self, name: &str) -> Result<(), LifecycleError> {
        let m = self.modules.get_mut(name).ok_or_else(|| LifecycleError::NotFound(name.into()))?;
        m.state = ModuleState::Stopped;
        tracing::info!("Module stopped: {}", name);
        Ok(())
    }

    pub fn restart(&mut self, name: &str) -> Result<(), LifecycleError> {
        self.stop(name)?;
        self.start(name)?;
        Ok(())
    }

    pub fn quarantine(&mut self, name: &str) -> Result<(), LifecycleError> {
        let m = self.modules.get_mut(name).ok_or_else(|| LifecycleError::NotFound(name.into()))?;
        m.state = ModuleState::Quarantined;
        tracing::warn!("Module quarantined: {}", name);
        Ok(())
    }

    pub fn list_modules(&self) -> Vec<ModuleInfo> {
        self.modules.values().cloned().collect()
    }

    pub fn get(&self, name: &str) -> Option<&ModuleInfo> {
        self.modules.get(name)
    }
}
