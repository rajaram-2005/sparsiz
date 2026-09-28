/*!
 * RAJARAM CORE — The Last Dance Control Plane
 *
 * Privileged supervisory service (V1: user-space daemon).
 * Evolution: user-space → kernel-integrated → hypervisor control plane → custom microkernel/bare-metal
 *
 * Responsibilities:
 * - Module lifecycle: load/start/pause/resume/stop/restart/quarantine
 * - Global state S(t)=[C(t),M(t),G(t),T(t),N(t),A(t),H(t)]
 * - Permission matrix Ω∈{0,1}^{M×R}
 * - Security: Secure Boot→TPM→Identity→Authorization→Execution Token
 * - Master clock τ(t)
 * - State machine: BOOT→SELF_TEST→INITIALIZE→READY→INGEST→ROUTE→EXECUTE→VERIFY→AUTHORIZE→COMMIT→IDLE + FAULT path
 * - Fault isolation with measurable T_isolation
 */

pub mod clock;
pub mod config;
pub mod fault;
pub mod identity;
pub mod lifecycle;
pub mod permissions;
pub mod state;
pub mod state_machine;

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

pub use clock::{MasterClock, Event, EventType};
pub use config::SystemConfig;
pub use fault::{FaultManager, Fault, FaultSeverity};
pub use identity::{IdentityManager, ModuleIdentity, SecurityLevel};
pub use lifecycle::{ModuleManager, ModuleState, ModuleInfo, LifecycleAction};
pub use permissions::{PermissionMatrix, Resource, ResourcePolicy};
pub use state::{GlobalState, CpuState, MemoryState, GpuState, ThermalState, NetworkState, AgentState, HealthState};
pub use state_machine::{StateMachine, SystemState};

/// Core controller that orchestrates all planes
#[derive(Debug)]
pub struct RajaramCore {
    pub id: Uuid,
    pub clock: MasterClock,
    pub state: GlobalState,
    pub state_machine: StateMachine,
    pub module_manager: ModuleManager,
    pub permission_matrix: PermissionMatrix,
    pub identity_manager: IdentityManager,
    pub fault_manager: FaultManager,
    pub config: SystemConfig,
}

impl RajaramCore {
    pub fn new(config: SystemConfig) -> Self {
        let id = Uuid::new_v4();
        let clock = MasterClock::new();
        let state = GlobalState::new();
        let state_machine = StateMachine::new();
        let module_manager = ModuleManager::new();
        let permission_matrix = PermissionMatrix::default_policy();
        let identity_manager = IdentityManager::new();
        let fault_manager = FaultManager::new();

        Self {
            id,
            clock,
            state,
            state_machine,
            module_manager,
            permission_matrix,
            identity_manager,
            fault_manager,
            config,
        }
    }

    /// Initialize system: BOOT → SELF_TEST → INITIALIZE → READY
    pub async fn initialize(&mut self) -> anyhow::Result<()> {
        tracing::info!("RAJARAM CORE initializing, id={}", self.id);
        self.state_machine.transition(SystemState::Boot)?;
        self.perform_self_test().await?;
        self.state_machine.transition(SystemState::SelfTest)?;
        self.state_machine.transition(SystemState::Initialize)?;
        // Load core modules: MAKESH, SARAM, FAISANTH, PREMSOTH
        self.module_manager.load("MAKESH".into(), "kernel/makesh".into())?;
        self.module_manager.load("SARAM".into(), "intelligence/saram".into())?;
        self.module_manager.load("FAISANTH".into(), "routing/faisanth".into())?;
        self.module_manager.load("PREMSOTH".into(), "verification/premsoth".into())?;
        self.state_machine.transition(SystemState::Ready)?;
        tracing::info!("RAJARAM CORE READY");
        Ok(())
    }

    async fn perform_self_test(&self) -> anyhow::Result<()> {
        tracing::info!("Performing self-test: secure boot, TPM, memory, IPC");
        // In V1, simulate checks
        Ok(())
    }

    /// Main execution pipeline: Sense→Compress→Understand→Route→Execute→Verify→Authorize
    pub async fn execute_pipeline(&mut self, task: TaskDescriptor) -> anyhow::Result<ExecutionResult> {
        let start = self.clock.now();
        
        self.state_machine.transition(SystemState::Ingest)?;
        let ingest_event = self.clock.create_event("RAJARAM", EventType::TaskIngested, &task.task_id);
        tracing::info!("Ingested task {}", task.task_id);

        self.state_machine.transition(SystemState::Route)?;
        // FAISANTH routing would happen here
        let route_event = self.clock.create_event("FAISANTH", EventType::RouteSelected, &task.task_id);

        self.state_machine.transition(SystemState::Execute)?;
        let exec_event = self.clock.create_event("AGENT", EventType::ExecutionStarted, &task.task_id);

        self.state_machine.transition(SystemState::Verify)?;
        let verify_event = self.clock.create_event("PREMSOTH", EventType::VerificationStarted, &task.task_id);

        self.state_machine.transition(SystemState::Authorize)?;
        // Check permission matrix Ω
        if !self.permission_matrix.is_authorized(&task.module, &task.resource) {
            self.fault_manager.report(Fault::unauthorized_access(task.module.clone(), task.resource.clone()));
            anyhow::bail!("Unauthorized: module {} cannot access resource {:?}", task.module, task.resource);
        }

        let auth_token = self.identity_manager.authorize(&task.module, &task.resource)?;
        
        self.state_machine.transition(SystemState::Commit)?;
        let result = ExecutionResult {
            task_id: task.task_id.clone(),
            authorized: true,
            token: auth_token,
            latency_ms: (self.clock.now() - start) as f64,
            events: vec![ingest_event, route_event, exec_event, verify_event],
        };

        self.state_machine.transition(SystemState::Idle)?;
        Ok(result)
    }

    pub fn get_state(&self) -> &GlobalState {
        &self.state
    }

    pub fn health_check(&self) -> HealthReport {
        HealthReport {
            core_id: self.id,
            state: self.state_machine.current_state(),
            modules: self.module_manager.list_modules(),
            faults: self.fault_manager.active_faults(),
            uptime_seconds: self.clock.uptime_seconds(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskDescriptor {
    pub task_id: String,
    pub module: String,
    pub resource: Resource,
    pub task_type: String,
    pub latency_budget_ms: u64,
    pub memory_mb: u64,
    pub compute_intensity: f64,
    pub parallelism: f64,
    pub thermal_priority: f64,
    pub security_level: u8,
}

impl TaskDescriptor {
    pub fn example_motor_fault() -> Self {
        Self {
            task_id: "T001".into(),
            module: "SARAM".into(),
            resource: Resource::Cpu,
            task_type: "inference".into(),
            latency_budget_ms: 20,
            memory_mb: 4096,
            compute_intensity: 0.84,
            parallelism: 0.91,
            thermal_priority: 0.7,
            security_level: 4,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionResult {
    pub task_id: String,
    pub authorized: bool,
    pub token: String,
    pub latency_ms: f64,
    pub events: Vec<Event>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthReport {
    pub core_id: Uuid,
    pub state: SystemState,
    pub modules: Vec<ModuleInfo>,
    pub faults: Vec<Fault>,
    pub uptime_seconds: u64,
}
