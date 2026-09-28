/*!
 * BFT Layer
 * If PREMSOTH is implemented as Byzantine fault-tolerant consensus, use established protocol rather than inventing threshold.
 * For classical Byzantine agreement under standard assumptions: N>=3f+1 where f is number of Byzantine nodes tolerated.
 * Define: proposal, validation, voting, quorum, commit, reject
 */

use crate::AgentOutput;
use crate::validation::ValidationResult;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConsensusConfig {
    pub f_tolerated: usize, // number of Byzantine nodes tolerated
    pub quorum_ratio: f64,
}

impl Default for ConsensusConfig {
    fn default() -> Self {
        Self {
            f_tolerated: 1, // tolerate 1 Byzantine with N=4, since N>=3f+1 => 4>=4
            quorum_ratio: 0.66,
        }
    }
}

impl ConsensusConfig {
    pub fn min_nodes_for_f(&self, f: usize) -> usize {
        3 * f + 1 // N>=3f+1
    }

    pub fn check_bft(&self, n: usize) -> bool {
        n >= self.min_nodes_for_f(self.f_tolerated)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentVote {
    pub agent_id: String,
    pub vote: bool,
    pub value: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConsensusResult {
    pub agreed_value: Option<serde_json::Value>,
    pub votes: Vec<AgentVote>,
    pub quorum_reached: bool,
    pub commit: bool,
    pub reason: String,
    pub bft_valid: bool,
}

impl ConsensusResult {
    pub fn rejected(reason: &str) -> Self {
        Self {
            agreed_value: None,
            votes: Vec::new(),
            quorum_reached: false,
            commit: false,
            reason: reason.to_string(),
            bft_valid: false,
        }
    }
}

#[derive(Debug)]
pub struct BftConsensus {
    config: ConsensusConfig,
}

impl BftConsensus {
    pub fn new(config: ConsensusConfig) -> Self {
        Self { config }
    }

    /// BFT consensus: proposal → validation → voting → quorum → commit/reject
    pub fn reach_consensus(&self, outputs: &[AgentOutput], validation: &ValidationResult) -> ConsensusResult {
        let n = outputs.len();
        let bft_valid = self.config.check_bft(n);
        
        if !bft_valid {
            tracing::warn!("BFT check failed: N={} < 3f+1={} for f={}", n, self.config.min_nodes_for_f(self.config.f_tolerated), self.config.f_tolerated);
        }

        // Proposal: select output with highest Score_i
        let best_agent = validation.scores.iter()
            .max_by(|a,b| a.1.partial_cmp(b.1).unwrap())
            .map(|(id, _)| id.clone());

        let agreed_value = if let Some(best_id) = &best_agent {
            outputs.iter().find(|o| &o.agent_id == best_id).map(|o| o.output.clone())
        } else {
            None
        };

        // Voting: agents vote if their output agrees with proposal within threshold
        let mut votes = Vec::new();
        if let Some(ref agreed) = agreed_value {
            for output in outputs {
                let sim = Self::value_similarity(&output.output, agreed);
                let vote = sim >= 0.7; // threshold
                votes.push(AgentVote {
                    agent_id: output.agent_id.clone(),
                    vote,
                    value: output.output.clone(),
                });
            }
        }

        let positive_votes = votes.iter().filter(|v| v.vote).count();
        let quorum_needed = (n as f64 * self.config.quorum_ratio).ceil() as usize;
        let quorum_reached = positive_votes >= quorum_needed;

        let commit = quorum_reached && bft_valid;
        let reason = if commit {
            format!("Quorum reached: {}/{} votes, BFT valid: N={}>=3f+1={}", positive_votes, n, n, self.config.min_nodes_for_f(self.config.f_tolerated))
        } else {
            format!("Quorum failed: {}/{} needed {}, BFT valid={}", positive_votes, n, quorum_needed, bft_valid)
        };

        ConsensusResult {
            agreed_value,
            votes,
            quorum_reached,
            commit,
            reason,
            bft_valid,
        }
    }

    fn value_similarity(a: &serde_json::Value, b: &serde_json::Value) -> f64 {
        if a == b {
            1.0
        } else if let (Some(a_f), Some(b_f)) = (a.as_f64(), b.as_f64()) {
            1.0 - (a_f - b_f).abs().min(1.0)
        } else {
            0.5
        }
    }
}
