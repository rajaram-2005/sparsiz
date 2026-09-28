/*!
 * Policy engine for PREMSOTH
 */

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RangeCheck {
    pub field: String,
    pub min: f64,
    pub max: f64,
}

impl RangeCheck {
    pub fn check(&self, value: f64) -> bool {
        value >= self.min && value <= self.max
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SafetyPolicy {
    pub name: String,
    pub range_checks: Vec<RangeCheck>,
    pub requires_human_approval: bool,
}

#[derive(Debug)]
pub struct PolicyEngine {
    policies: Vec<SafetyPolicy>,
}

impl PolicyEngine {
    pub fn new() -> Self {
        let policies = vec![
            SafetyPolicy {
                name: "voltage".into(),
                range_checks: vec![RangeCheck { field: "voltage".into(), min: 0.0, max: 480.0 }],
                requires_human_approval: false,
            },
            SafetyPolicy {
                name: "current".into(),
                range_checks: vec![RangeCheck { field: "current".into(), min: 0.0, max: 100.0 }],
                requires_human_approval: false,
            },
            SafetyPolicy {
                name: "temperature".into(),
                range_checks: vec![RangeCheck { field: "temperature".into(), min: -40.0, max: 150.0 }],
                requires_human_approval: false,
            },
            SafetyPolicy {
                name: "actuator".into(),
                range_checks: vec![
                    RangeCheck { field: "actuator_command".into(), min: -100.0, max: 100.0 },
                ],
                requires_human_approval: true, // safety-critical needs human/authorized controller
            },
        ];
        Self { policies }
    }

    pub fn evaluate(&self, output: &serde_json::Value) -> (bool, String) {
        if let serde_json::Value::Object(map) = output {
            for policy in &self.policies {
                for check in &policy.range_checks {
                    if let Some(val) = map.get(&check.field) {
                        if let Some(f) = val.as_f64() {
                            if !check.check(f) {
                                return (false, format!("Policy {} failed: {}={} out of range [{}, {}]", policy.name, check.field, f, check.min, check.max));
                            }
                        }
                    }
                }
            }
        }
        (true, "All policies passed".into())
    }
}
