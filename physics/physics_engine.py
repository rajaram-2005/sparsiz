"""
PHYSICS ENGINE — PINN concept

Data → Neural Model → Physics Constraint → Loss → Optimization

L = L_data + λ L_physics

Possible domains: electrical, mechanical, thermal, fluid, power systems, motors, power electronics, robotics

Physics: P=VI, S=P+jQ, P_mech=Tω, mẍ+cẋ+kx=F(t)
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import math

@dataclass
class PhysicsDomain:
    name: str
    equations: List[str]

class PhysicsEngine:
    def __init__(self):
        self.domains = {
            "electrical": PhysicsDomain("electrical", ["P=VI", "S=P+jQ", "V=IR"]),
            "mechanical": PhysicsDomain("mechanical", ["P_mech=Tω", "F=ma", "mẍ+cẋ+kx=F(t)"]),
            "thermal": PhysicsDomain("thermal", ["Q=mcΔT", "P=I²R thermal"]),
            "fluid": PhysicsDomain("fluid", ["Bernoulli", "Navier-Stokes"]),
            "power_systems": PhysicsDomain("power_systems", ["Y=G+jB", "P=VI", "S=P+jQ"]),
            "motors": PhysicsDomain("motors", ["P_mech=Tω", "V=IR+E_backEMF"]),
            "power_electronics": PhysicsDomain("power_electronics", ["P=VI", "switching loss"]),
            "robotics": PhysicsDomain("robotics", ["F=ma", "τ=Iα", "mẍ+cẋ+kx=F(t)"]),
        }

    def physics_loss(self, sample: Dict[str, float], domain: str) -> float:
        """
        L_physics encourages model to respect physics constraints
        """
        loss = 0.0

        if domain in ["electrical", "power_systems", "power_electronics"]:
            if "voltage" in sample and "current" in sample and "power" in sample:
                expected = sample["voltage"] * sample["current"]  # P=VI
                loss += (expected - sample["power"])**2 / (expected**2+1e-6)

            if "real_power" in sample and "reactive_power" in sample and "apparent_power_real" in sample:
                # S=P+jQ, |S|=sqrt(P²+Q²)
                expected_mag = math.sqrt(sample["real_power"]**2 + sample["reactive_power"]**2)
                actual_mag = abs(complex(sample["apparent_power_real"], sample.get("apparent_power_imag",0)))
                loss += (expected_mag - actual_mag)**2

        if domain in ["mechanical", "motors", "robotics"]:
            if "torque" in sample and "omega" in sample and "mech_power" in sample:
                expected = sample["torque"] * sample["omega"]  # P_mech=Tω
                loss += (expected - sample["mech_power"])**2 / (expected**2+1e-6)

            if all(k in sample for k in ["m","c","k","x","x_dot","x_ddot","F"]):
                # mẍ+cẋ+kx=F(t)
                expected_F = sample["m"]*sample["x_ddot"] + sample["c"]*sample["x_dot"] + sample["k"]*sample["x"]
                loss += (expected_F - sample["F"])**2

        return loss

    def total_loss(self, data_loss: float, physics_loss: float, lambda_physics: float = 0.5) -> float:
        # L = L_data + λ L_physics
        return data_loss + lambda_physics * physics_loss

    def evaluate(self, samples: List[Dict[str, float]], domain: str) -> Dict[str, float]:
        total_physics = 0.0
        for s in samples:
            total_physics += self.physics_loss(s, domain)

        avg_physics = total_physics / len(samples) if samples else 0
        return {
            "domain": domain,
            "physics_loss": avg_physics,
            "equations": self.domains[domain].equations,
            "consistent": avg_physics < 0.1,
        }

class DigitalTwinEngine:
    """
    Physical System → Sensor Data → Digital Twin → Simulation → AI Agent → Prediction
    AI should be tested in digital twin before physical execution
    """
    def __init__(self, physics_engine: PhysicsEngine):
        self.physics = physics_engine
        self.twin_state: Dict[str, Any] = {}

    def update_from_sensors(self, sensor_data: Dict[str, float]):
        self.twin_state.update(sensor_data)
        print(f"Digital Twin updated from sensors: {sensor_data}")

    def simulate(self, action: Dict[str, Any]) -> Dict[str, float]:
        # Simulate future state in twin
        future = self.twin_state.copy()
        if "voltage_command" in action:
            future["voltage"] = action["voltage_command"]
            future["power"] = future["voltage"] * future.get("current", 14.2)

        print(f"Digital Twin simulation for action {action}: future={future}")
        return future

    def test_ai_before_physical(self, ai_command: Dict[str, Any]) -> bool:
        # Test AI command in twin before physical execution
        future = self.simulate(ai_command)

        # Check physics consistency
        physics_loss = self.physics.physics_loss(future, "electrical")
        safe = physics_loss < 0.5 and future.get("temperature", 0) < 150

        print(f"AI command {ai_command} tested in twin: physics_loss={physics_loss:.3f}, safe={safe}")
        return safe

from typing import Any

if __name__ == "__main__":
    engine = PhysicsEngine()

    samples = [
        {"voltage": 400, "current": 14.2, "power": 5680, "torque": 50, "omega": 155, "mech_power": 7750},
        {"voltage": 400, "current": 16.0, "power": 6400, "torque": 55, "omega": 150, "mech_power": 8250},
        {"voltage": 400, "current": 14.2, "power": 5000, "torque": 50, "omega": 155, "mech_power": 7750},  # inconsistent P=VI
    ]

    for domain in ["electrical", "mechanical"]:
        result = engine.evaluate(samples, domain)
        print(f"Domain {domain}: physics_loss={result['physics_loss']:.3f}, consistent={result['consistent']}, equations={result['equations']}")

    print("\n=== Digital Twin ===")
    twin = DigitalTwinEngine(engine)
    twin.update_from_sensors({"voltage": 400, "current": 14.2, "temperature": 81, "vibration": 8.3})
    twin.test_ai_before_physical({"voltage_command": 410})
    twin.test_ai_before_physical({"voltage_command": 600})  # unsafe
