/*!
 * PREMSOTH — Deterministic verification and authorization layer for multi-agent outputs
 * Not "mathematical hallucination eliminator" — no general architecture guarantees elimination.
 * 
 * Architecture: Task → Agents A/B/C → Outputs → PREMSOTH → Semantic/Physics/Policy checks → Decision
 * Verification: a_i=f_i(x), Agreement A_ij=sim(a_i,a_j), Confidence C_i=P(a_i|x), Reliability R_i historical
 * Score_i = w_a A_i + w_c C_i + w_r R_i + w_p P_i
 * BFT: N>=3f+1, proposal/validation/voting/quorum/commit/reject
 * Safety: AI→PREMSOTH→Safety policy→Range→Interlock→Human/authorized controller→PLC
 * Metrics: FAR, FRR, consensus accuracy A_c
 */

pub mod consensus;
pub mod validation;
pub mod policy;
pub mod safety;

pub use consensus::{BftConsensus, ConsensusConfig, ConsensusResult, AgentVote};
pub use validation::{Validator, ValidationResult, AgreementMetric, SimilarityMethod};
pub use policy::{PolicyEngine, SafetyPolicy, RangeCheck};
pub use safety::{SafetyGate, SafetyCheckResult, SafetyLimits};

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentOutput {
    pub agent_id: String,
    pub task_id: String,
    pub output: serde_json::Value,
    pub confidence: f64, // C_i = P(a_i|x)
    pub reliability: f64, // R_i historical
    pub timestamp: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationConfig {
    pub w_agreement: f64,
    pub w_confidence: f64,
    pub w_reliability: f64,
    pub w_physics: f64,
    pub min_agents: usize,
    pub similarity_threshold: f64,
}

impl Default for VerificationConfig {
    fn default() -> Self {
        Self {
            w_agreement: 0.35,
            w_confidence: 0.25,
            w_reliability: 0.2,
            w_physics: 0.2,
            min_agents: 3,
            similarity_threshold: 0.7,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationDecision {
    pub task_id: String,
    pub agreed_output: Option<serde_json::Value>,
    pub confidence: f64,
    pub agreement_score: f64,
    pub scores: HashMap<String, f64>, // Score_i
    pub verified: bool,
    pub reason: String,
    pub consensus: ConsensusResult,
    pub safety_check: SafetyCheckResult,
}

#[derive(Debug)]
pub struct Premsoth {
    pub config: VerificationConfig,
    pub validator: Validator,
    pub consensus: BftConsensus,
    pub policy_engine: PolicyEngine,
    pub safety_gate: SafetyGate,
}

impl Premsoth {
    pub fn new(config: VerificationConfig) -> Self {
        Self {
            validator: Validator::new(config.clone()),
            consensus: BftConsensus::new(ConsensusConfig::default()),
            policy_engine: PolicyEngine::new(),
            safety_gate: SafetyGate::new(SafetyLimits::default()),
            config,
        }
    }

    /// Main verification pipeline
    /// Task → Agents → Outputs → PREMSOTH → Semantic/Physics/Policy → Decision
    pub fn verify(&self, task_id: &str, outputs: Vec<AgentOutput>) -> VerificationDecision {
        tracing::info!("PREMSOTH verifying task {} with {} agents", task_id, outputs.len());

        if outputs.len() < self.config.min_agents {
            return VerificationDecision {
                task_id: task_id.to_string(),
                agreed_output: None,
                confidence: 0.0,
                agreement_score: 0.0,
                scores: HashMap::new(),
                verified: false,
                reason: format!("Insufficient agents: {} < {}", outputs.len(), self.config.min_agents),
                consensus: ConsensusResult::rejected("insufficient agents"),
                safety_check: SafetyCheckResult::not_applicable(),
            };
        }

        // 1. Semantic, Physics, Policy checks
        let validation = self.validator.validate(&outputs);
        
        // 2. BFT consensus N>=3f+1
        let consensus = self.consensus.reach_consensus(&outputs, &validation);

        // 3. Safety gate: Range checking, Interlock checking
        let safety_check = if let Some(ref agreed) = consensus.agreed_value {
            self.safety_gate.check(agreed)
        } else {
            SafetyCheckResult::failed("No agreed value for safety check")
        };

        // 4. Final decision
        let verified = validation.overall_agreement >= self.config.similarity_threshold
            && consensus.quorum_reached
            && safety_check.passed;

        let reason = if verified {
            format!("Verified: agreement={:.2}, quorum={}, safety={}", validation.overall_agreement, consensus.quorum_reached, safety_check.passed)
        } else {
            format!("Rejected: agreement={:.2} (threshold {}), quorum={}, safety={} - {}", 
                validation.overall_agreement, self.config.similarity_threshold, consensus.quorum_reached, safety_check.passed, safety_check.reason)
        };

        VerificationDecision {
            task_id: task_id.to_string(),
            agreed_output: consensus.agreed_value.clone(),
            confidence: validation.avg_confidence,
            agreement_score: validation.overall_agreement,
            scores: validation.scores.clone(),
            verified,
            reason,
            consensus,
            safety_check,
        }
    }

    /// Benchmark: FAR, FRR, consensus accuracy
    pub fn benchmark(&self, test_cases: Vec<(Vec<AgentOutput>, bool)>) -> BenchmarkMetrics {
        let mut correct_decisions = 0;
        let mut false_accept = 0;
        let mut false_reject = 0;
        let mut total_incorrect = 0;
        let mut total_correct = 0;

        for (outputs, should_be_valid) in &test_cases {
            let decision = self.verify("BENCH", outputs.clone());
            let is_correct = decision.verified == *should_be_valid;
            if is_correct {
                correct_decisions += 1;
            }

            if *should_be_valid {
                total_correct += 1;
                if !decision.verified {
                    false_reject += 1;
                }
            } else {
                total_incorrect += 1;
                if decision.verified {
                    false_accept += 1;
                }
            }
        }

        BenchmarkMetrics {
            total_cases: test_cases.len(),
            correct_decisions,
            accuracy: correct_decisions as f64 / test_cases.len() as f64,
            far: if total_incorrect > 0 { false_accept as f64 / total_incorrect as f64 } else { 0.0 },
            frr: if total_correct > 0 { false_reject as f64 / total_correct as f64 } else { 0.0 },
            false_accept,
            false_reject,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BenchmarkMetrics {
    pub total_cases: usize,
    pub correct_decisions: usize,
    pub accuracy: f64, // A_c = correct decisions / total decisions
    pub far: f64, // FAR = incorrect accepted / total incorrect
    pub frr: f64, // FRR = correct rejected / total correct
    pub false_accept: usize,
    pub false_reject: usize,
}

impl Default for Premsoth {
    fn default() -> Self {
        Self::new(VerificationConfig::default())
    }
}
