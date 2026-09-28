/*!
 * Global State Machine
 * BOOT→SELF_TEST→INITIALIZE→READY→INGEST→ROUTE→EXECUTE→VERIFY→AUTHORIZE→COMMIT→IDLE
 * ANY STATE→FAULT→ISOLATE→DIAGNOSE→recover/terminate
 */

use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum SystemState {
    Boot,
    SelfTest,
    Initialize,
    Ready,
    Ingest,
    Route,
    Execute,
    Verify,
    Authorize,
    Commit,
    Idle,
    Fault,
    Isolate,
    Diagnose,
    Quarantine,
    Terminate,
}

#[derive(Debug, Error)]
pub enum StateTransitionError {
    #[error("Invalid transition from {from:?} to {to:?}")]
    InvalidTransition { from: SystemState, to: SystemState },
}

#[derive(Debug, Clone)]
pub struct StateMachine {
    current: SystemState,
    history: Vec<SystemState>,
}

impl StateMachine {
    pub fn new() -> Self {
        Self {
            current: SystemState::Boot,
            history: vec![SystemState::Boot],
        }
    }

    pub fn current_state(&self) -> SystemState {
        self.current
    }

    pub fn transition(&mut self, to: SystemState) -> Result<(), StateTransitionError> {
        if self.is_valid_transition(self.current, to) || to == SystemState::Fault {
            // Fault can happen from ANY STATE
            tracing::info!("State transition: {:?} → {:?}", self.current, to);
            self.current = to;
            self.history.push(to);
            Ok(())
        } else {
            Err(StateTransitionError::InvalidTransition {
                from: self.current,
                to,
            })
        }
    }

    fn is_valid_transition(&self, from: SystemState, to: SystemState) -> bool {
        use SystemState::*;
        matches!(
            (from, to),
            (Boot, SelfTest)
                | (SelfTest, Initialize)
                | (Initialize, Ready)
                | (Ready, Ingest)
                | (Ingest, Route)
                | (Route, Execute)
                | (Execute, Verify)
                | (Verify, Authorize)
                | (Verify, Quarantine) // FAIL path
                | (Authorize, Commit)
                | (Commit, Idle)
                | (Idle, Ingest)
                | (Idle, Ready)
                | (Fault, Isolate)
                | (Isolate, Diagnose)
                | (Diagnose, Ready) // recover
                | (Diagnose, Terminate) // terminate
                | (Quarantine, Diagnose)
                | (Ready, Ready) // idempotent
                | (Idle, Idle)
                | (Boot, Boot)
        )
    }

    pub fn history(&self) -> &[SystemState] {
        &self.history
    }

    pub fn is_terminal(&self) -> bool {
        matches!(self.current, SystemState::Terminate)
    }

    pub fn is_ready(&self) -> bool {
        matches!(self.current, SystemState::Ready | SystemState::Idle)
    }
}

impl Default for StateMachine {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_valid_flow() {
        let mut sm = StateMachine::new();
        assert_eq!(sm.current_state(), SystemState::Boot);
        sm.transition(SystemState::SelfTest).unwrap();
        sm.transition(SystemState::Initialize).unwrap();
        sm.transition(SystemState::Ready).unwrap();
        sm.transition(SystemState::Ingest).unwrap();
        sm.transition(SystemState::Route).unwrap();
        sm.transition(SystemState::Execute).unwrap();
        sm.transition(SystemState::Verify).unwrap();
        sm.transition(SystemState::Authorize).unwrap();
        sm.transition(SystemState::Commit).unwrap();
        sm.transition(SystemState::Idle).unwrap();
    }

    #[test]
    fn test_fault_from_any() {
        let mut sm = StateMachine::new();
        sm.transition(SystemState::SelfTest).unwrap();
        sm.transition(SystemState::Fault).unwrap(); // allowed from any
        assert_eq!(sm.current_state(), SystemState::Fault);
        sm.transition(SystemState::Isolate).unwrap();
        sm.transition(SystemState::Diagnose).unwrap();
        sm.transition(SystemState::Ready).unwrap(); // recover
    }

    #[test]
    fn test_fail_to_quarantine() {
        let mut sm = StateMachine::new();
        sm.transition(SystemState::SelfTest).unwrap();
        sm.transition(SystemState::Initialize).unwrap();
        sm.transition(SystemState::Ready).unwrap();
        sm.transition(SystemState::Ingest).unwrap();
        sm.transition(SystemState::Route).unwrap();
        sm.transition(SystemState::Execute).unwrap();
        sm.transition(SystemState::Verify).unwrap();
        sm.transition(SystemState::Quarantine).unwrap(); // FAIL path
    }
}
