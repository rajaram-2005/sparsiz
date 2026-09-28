/*!
 * RAJARAM Daemon — privileged supervisory service (V1 user-space)
 * Later evolves to kernel-integrated → hypervisor control plane → microkernel
 */

use rajaram_core::{RajaramCore, SystemConfig, TaskDescriptor};
use tracing_subscriber::EnvFilter;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env().add_directive("info".parse().unwrap()))
        .init();

    println!("=== RAJARAM CORE Daemon v0.6.0 ===");
    println!("The Last Dance — Control Plane");
    println!("Mode: research prototype (Linux user-space)");

    let config = SystemConfig::default_config();
    println!("Config: system={}, mode={}", config.system.name, config.system.mode);
    println!("Permission Matrix Ω:\n{}", rajaram_core::permissions::PermissionMatrix::default_policy().matrix_as_table());

    let mut core = RajaramCore::new(config);
    core.initialize().await?;

    // Simulate pipeline
    println!("\n--- Executing example pipeline ---");
    let task = TaskDescriptor::example_motor_fault();
    match core.execute_pipeline(task).await {
        Ok(result) => {
            println!("Pipeline executed: task_id={}, authorized={}, latency={:.2}ms", result.task_id, result.authorized, result.latency_ms);
            println!("Events:");
            for ev in result.events {
                println!("  [{:?}] {} seq={} hash={}", ev.event_type, ev.module, ev.sequence, ev.payload_hash);
            }
        }
        Err(e) => {
            eprintln!("Pipeline failed: {}", e);
        }
    }

    let health = core.health_check();
    println!("\n--- Health Report ---");
    println!("Core ID: {}", health.core_id);
    println!("State: {:?}", health.state);
    println!("Modules: {:?}", health.modules.iter().map(|m| &m.name).collect::<Vec<_>>());
    println!("Uptime: {}s", health.uptime_seconds);
    println!("Active faults: {}", health.faults.len());

    println!("\nRAJARAM CORE daemon running. Press Ctrl+C to exit.");
    // In real daemon, would start gRPC server, Prometheus metrics, etc.
    // For V1, just run health loop
    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
        let h = core.health_check();
        tracing::info!("Health check: state={:?}, modules={}, faults={}", h.state, h.modules.len(), h.faults.len());
    }
}
