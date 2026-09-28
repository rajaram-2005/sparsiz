/*!
 * RAJARAM Security Architecture
 * Secure Boot → TPM → RAJARAM Identity → Module Identity + Resource Policy → Authorization → Execution Token
 * Future PQC: ML-KEM (FIPS 203), ML-DSA (FIPS 204), SLH-DSA (FIPS 205)
 */

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum SecurityLevel {
    Low = 1,
    Medium = 2,
    High = 3,
    Critical = 4,
    SafetyCritical = 5,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModuleIdentity {
    pub id: Uuid,
    pub name: String,
    pub version: String,
    pub security_level: SecurityLevel,
    pub public_key_hash: String,
    pub signed: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionToken {
    pub token_id: Uuid,
    pub module: String,
    pub resource: String,
    pub issued_at: u64,
    pub expires_at: u64,
    pub signature: String,
}

#[derive(Debug, Default)]
pub struct IdentityManager {
    identities: HashMap<String, ModuleIdentity>,
    tokens: HashMap<Uuid, ExecutionToken>,
}

impl IdentityManager {
    pub fn new() -> Self {
        Self {
            identities: HashMap::new(),
            tokens: HashMap::new(),
        }
    }

    pub fn register_module(&mut self, name: String, security_level: SecurityLevel) -> ModuleIdentity {
        let identity = ModuleIdentity {
            id: Uuid::new_v4(),
            name: name.clone(),
            version: "0.6.0".into(),
            security_level,
            public_key_hash: format!("hash-{}", name),
            signed: true,
        };
        self.identities.insert(name, identity.clone());
        tracing::info!("Registered module identity: {} {:?}", identity.name, identity.id);
        identity
    }

    /// Authorization: Module Identity + Resource Policy → Execution Token
    pub fn authorize(&mut self, module: &str, resource: &crate::permissions::Resource) -> anyhow::Result<String> {
        // Check identity exists
        if !self.identities.contains_key(module) {
            // Auto-register for V1 prototype
            self.register_module(module.to_string(), SecurityLevel::Medium);
        }

        let token = ExecutionToken {
            token_id: Uuid::new_v4(),
            module: module.to_string(),
            resource: format!("{:?}", resource),
            issued_at: 0,
            expires_at: 3600,
            signature: format!("sig-{}-{:?}", module, resource),
        };
        let token_str = token.token_id.to_string();
        self.tokens.insert(token.token_id, token);
        tracing::info!("Authorized {} for {:?}, token {}", module, resource, token_str);
        Ok(token_str)
    }

    pub fn verify_token(&self, token_str: &str) -> bool {
        if let Ok(uuid) = Uuid::parse_str(token_str) {
            self.tokens.contains_key(&uuid)
        } else {
            false
        }
    }

    pub fn list_identities(&self) -> Vec<ModuleIdentity> {
        self.identities.values().cloned().collect()
    }
}
