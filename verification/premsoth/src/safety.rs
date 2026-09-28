/*!
 * Safety-Critical Execution
 * Never LLM→PREMSOTH→PLC without independent safety layer
 * Correct: AI recommendation→PREMSOTH→Safety policy engine→Range checking→Interlock checking→Human/authorized controller→PLC
 * Example: Vmin≤Vcommand≤Vmax, Icommand≤Imax, T<Tcritical
 */

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SafetyLimits {
    pub v_min: f64,
    pub v_max: f64,
    pub i_max: f64,
    pub t_critical: f64,
    pub actuator_min: f64,
    pub actuator_max: f64,
}

impl Default for SafetyLimits {
    fn default() -> Self {
        Self {
            v_min: 0.0,
            v_max: 480.0,
            i_max: 100.0,
            t_critical: 150.0,
            actuator_min: -100.0,
            actuator_max: 100.0,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SafetyCheckResult {
    pub passed: bool,
    pub reason: String,
    pub checks: Vec<(String, bool)>,
}

impl SafetyCheckResult {
    pub fn passed(reason: &str) -> Self {
        Self {
            passed: true,
            reason: reason.to_string(),
            checks: vec![],
        }
    }

    pub fn failed(reason: &str) -> Self {
        Self {
            passed: false,
            reason: reason.to_string(),
            checks: vec![],
        }
    }

    pub fn not_applicable() -> Self {
        Self {
            passed: true,
            reason: "No safety-critical command, not applicable".into(),
            checks: vec![],
        }
    }
}

#[derive(Debug)]
pub struct SafetyGate {
    limits: SafetyLimits,
}

impl SafetyGate {
    pub fn new(limits: SafetyLimits) -> Self {
        Self { limits }
    }

    /// Safety check: Vmin≤Vcmd≤Vmax, Icmd≤Imax, T<Tcritical
    pub fn check(&self, output: &serde_json::Value) -> SafetyCheckResult {
        let mut checks = Vec::new();
        let mut passed = true;
        let mut reasons = Vec::new();

        if let serde_json::Value::Object(map) = output {
            // Check voltage: Vmin≤Vcommand≤Vmax
            if let Some(v) = map.get("voltage").or_else(|| map.get("V_command")).or_else(|| map.get("v_command")) {
                if let Some(voltage) = v.as_f64() {
                    let ok = voltage >= self.limits.v_min && voltage <= self.limits.v_max;
                    checks.push((format!("Voltage {} in [{}, {}]", voltage, self.limits.v_min, self.limits.v_max), ok));
                    if !ok {
                        passed = false;
                        reasons.push(format!("Voltage {} out of range", voltage));
                    }
                }
            }

            // Check current: Icommand≤Imax
            if let Some(i) = map.get("current").or_else(|| map.get("I_command")).or_else(|| map.get("i_command")) {
                if let Some(current) = i.as_f64() {
                    let ok = current <= self.limits.i_max;
                    checks.push((format!("Current {} ≤ {}", current, self.limits.i_max), ok));
                    if !ok {
                        passed = false;
                        reasons.push(format!("Current {} exceeds Imax {}", current, self.limits.i_max));
                    }
                }
            }

            // Check temperature: T<Tcritical
            if let Some(t) = map.get("temperature").or_else(|| map.get("T")) {
                if let Some(temp) = t.as_f64() {
                    let ok = temp < self.limits.t_critical;
                    checks.push((format!("Temperature {} < {}", temp, self.limits.t_critical), ok));
                    if !ok {
                        passed = false;
                        reasons.push(format!("Temperature {} exceeds Tcritical {}", temp, self.limits.t_critical));
                    }
                }
            }

            // Check actuator
            if let Some(a) = map.get("actuator_command").or_else(|| map.get("actuator")) {
                if let Some(act) = a.as_f64() {
                    let ok = act >= self.limits.actuator_min && act <= self.limits.actuator_max;
                    checks.push((format!("Actuator {} in [{}, {}]", act, self.limits.actuator_min, self.limits.actuator_max), ok));
                    if !ok {
                        passed = false;
                        reasons.push(format!("Actuator command {} out of range", act));
                    }
                }
            }

            // If no safety-critical fields, not applicable = pass
            if checks.is_empty() {
                return SafetyCheckResult::not_applicable();
            }
        } else {
            return SafetyCheckResult::not_applicable();
        }

        if passed {
            SafetyCheckResult {
                passed: true,
                reason: "All safety checks passed: Vmin≤Vcmd≤Vmax, Icmd≤Imax, T<Tcritical".into(),
                checks,
            }
        } else {
            SafetyCheckResult {
                passed: false,
                reason: reasons.join("; "),
                checks,
            }
        }
    }

    /// Interlock checking (simplified)
    pub fn check_interlock(&self, output: &serde_json::Value) -> bool {
        // In real industrial system, check interlocks independent of AI
        // Example: motor cannot start if guard open, etc.
        // For prototype, always true unless explicitly fails
        if let serde_json::Value::Object(map) = output {
            if let Some(interlock) = map.get("interlock") {
                if interlock == false {
                    return false;
                }
            }
        }
        true
    }
}
