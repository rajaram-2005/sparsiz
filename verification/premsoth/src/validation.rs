/*!
 * PREMSOTH Validation
 * For each agent: a_i=f_i(x)
 * Agreement A_ij=sim(a_i,a_j) where sim could be cosine, probability divergence, semantic, structured-output comparison
 * Confidence C_i=P(a_i|x), Reliability R_i historical
 * Score_i = w_a A_i + w_c C_i + w_r R_i + w_p P_i
 */

use crate::{AgentOutput, VerificationConfig};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SimilarityMethod {
    Cosine,
    ProbabilityDivergence,
    Semantic,
    StructuredOutput,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgreementMetric {
    pub agent_i: String,
    pub agent_j: String,
    pub similarity: f64, // A_ij
    pub method: SimilarityMethod,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationResult {
    pub agreements: Vec<AgreementMetric>,
    pub overall_agreement: f64,
    pub avg_confidence: f64,
    pub scores: HashMap<String, f64>, // Score_i
    pub physics_consistent: bool,
}

#[derive(Debug)]
pub struct Validator {
    config: VerificationConfig,
}

impl Validator {
    pub fn new(config: VerificationConfig) -> Self {
        Self { config }
    }

    pub fn validate(&self, outputs: &[AgentOutput]) -> ValidationResult {
        let mut agreements = Vec::new();
        let mut total_sim = 0.0;
        let mut count = 0;

        // Calculate A_ij = sim(a_i, a_j) for all pairs
        for i in 0..outputs.len() {
            for j in (i+1)..outputs.len() {
                let sim = self.similarity(&outputs[i], &outputs[j]);
                total_sim += sim;
                count += 1;
                agreements.push(AgreementMetric {
                    agent_i: outputs[i].agent_id.clone(),
                    agent_j: outputs[j].agent_id.clone(),
                    similarity: sim,
                    method: SimilarityMethod::StructuredOutput,
                });
            }
        }

        let overall_agreement = if count > 0 { total_sim / count as f64 } else { 0.0 };
        let avg_confidence = outputs.iter().map(|o| o.confidence).sum::<f64>() / outputs.len() as f64;

        // Calculate Score_i = w_a A_i + w_c C_i + w_r R_i + w_p P_i
        let mut scores = HashMap::new();
        for output in outputs {
            // A_i: average agreement of this agent with others
            let a_i = agreements.iter()
                .filter(|a| a.agent_i == output.agent_id || a.agent_j == output.agent_id)
                .map(|a| a.similarity)
                .sum::<f64>() / (outputs.len() - 1).max(1) as f64;

            let c_i = output.confidence;
            let r_i = output.reliability;
            let p_i = self.physics_consistency(output); // P_i physics/policy consistency

            let score = self.config.w_agreement * a_i
                + self.config.w_confidence * c_i
                + self.config.w_reliability * r_i
                + self.config.w_physics * p_i;

            scores.insert(output.agent_id.clone(), score);
        }

        ValidationResult {
            agreements,
            overall_agreement,
            avg_confidence,
            scores,
            physics_consistent: true, // simplified
        }
    }

    fn similarity(&self, a: &AgentOutput, b: &AgentOutput) -> f64 {
        // Structured output comparison: if both have same fault probability within threshold, high similarity
        // In real: cosine similarity, probability divergence, semantic similarity
        match (&a.output, &b.output) {
            (serde_json::Value::Object(map_a), serde_json::Value::Object(map_b)) => {
                // Example: compare "fault_probability" fields
                if let (Some(p_a), Some(p_b)) = (map_a.get("fault_probability"), map_b.get("fault_probability")) {
                    if let (Some(f_a), Some(f_b)) = (p_a.as_f64(), p_b.as_f64()) {
                        return 1.0 - (f_a - f_b).abs(); // high if close
                    }
                }
                // Compare string outputs
                if a.output == b.output {
                    1.0
                } else {
                    0.5
                }
            }
            _ => {
                if a.output == b.output { 1.0 } else { 0.3 }
            }
        }
    }

    fn physics_consistency(&self, output: &AgentOutput) -> f64 {
        // Check P=VI, S=P+jQ, P_mech=Tω, mẍ+cẋ+kx=F(t) etc
        // For prototype, check if output values are physically plausible
        if let serde_json::Value::Object(map) = &output.output {
            if let Some(v) = map.get("voltage") {
                if let Some(voltage) = v.as_f64() {
                    if voltage < 0.0 || voltage > 1000.0 {
                        return 0.0; // implausible
                    }
                }
            }
            if let Some(t) = map.get("temperature") {
                if let Some(temp) = t.as_f64() {
                    if temp > 200.0 {
                        return 0.2;
                    }
                }
            }
        }
        1.0 // consistent
    }
}
