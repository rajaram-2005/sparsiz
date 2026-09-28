/*!
 * Master Clock τ(t)
 * Every event: timestamp, module_id, sequence_id, event_type, payload_hash
 * Distinguish physical, monotonic, logical, synchronization clocks
 */

use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{SystemTime, UNIX_EPOCH, Instant};

static SEQUENCE: AtomicU64 = AtomicU64::new(0);

#[derive(Debug, Clone)]
pub struct MasterClock {
    start_instant: Instant,
    start_system: SystemTime,
    epoch_offset: u64,
}

impl MasterClock {
    pub fn new() -> Self {
        Self {
            start_instant: Instant::now(),
            start_system: SystemTime::now(),
            epoch_offset: 0,
        }
    }

    /// τ(t) - system epoch monotonic
    pub fn now(&self) -> u64 {
        self.start_instant.elapsed().as_millis() as u64 + self.epoch_offset
    }

    pub fn system_time_ms(&self) -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64
    }

    pub fn uptime_seconds(&self) -> u64 {
        self.start_instant.elapsed().as_secs()
    }

    pub fn create_event(&self, module: &str, event_type: EventType, payload: &str) -> Event {
        let seq = SEQUENCE.fetch_add(1, Ordering::SeqCst);
        let timestamp = self.now();
        let hash = format!("{:x}", md5_hash(payload));
        
        Event {
            timestamp,
            module: module.to_string(),
            sequence: seq,
            event_type,
            payload_hash: hash,
            system_time: self.system_time_ms(),
        }
    }
}

fn md5_hash(s: &str) -> u64 {
    // Simple hash for demo, not cryptographic - use sha256 in production
    let mut h: u64 = 0xcbf29ce484222325;
    for b in s.bytes() {
        h ^= b as u64;
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    pub timestamp: u64, // τ(t) logical clock
    pub module: String,
    pub sequence: u64,
    pub event_type: EventType,
    pub payload_hash: String,
    pub system_time: u64, // physical clock
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EventType {
    TaskIngested,
    LatentVectorReady,
    RouteSelected,
    ExecutionStarted,
    ExecutionFinished,
    VerificationStarted,
    VerificationFinished,
    SafetyCheckPassed,
    SafetyCheckFailed,
    Authorized,
    Committed,
    FaultDetected,
    ModuleLoaded,
    ModuleStarted,
    ModuleStopped,
    Quarantined,
}

impl Default for MasterClock {
    fn default() -> Self {
        Self::new()
    }
}
