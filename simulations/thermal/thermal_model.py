"""
Thermal model T_i(t) for every monitored device i
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import math
import random
import time

class ThermalModel:
    def __init__(self):
        self.devices = {
            "CPU-1": {"temp": 60.0, "power": 65.0, "thermal_resistance": 0.5, "capacitance": 10.0},
            "CPU-2": {"temp": 65.0, "power": 65.0, "thermal_resistance": 0.5, "capacitance": 10.0},
            "GPU-1": {"temp": 75.0, "power": 150.0, "thermal_resistance": 0.3, "capacitance": 15.0},
            "GPU-2": {"temp": 78.0, "power": 150.0, "thermal_resistance": 0.3, "capacitance": 15.0},
            "NPU-1": {"temp": 55.0, "power": 10.0, "thermal_resistance": 0.8, "capacitance": 5.0},
        }
        self.ambient = 25.0

    def update(self, dt: float = 1.0):
        """
        Simple thermal model: dT/dt = (P * R_th - (T - T_ambient)) / (R_th * C_th)
        """
        for dev, state in self.devices.items():
            p = state["power"]
            r = state["thermal_resistance"]
            c = state["capacitance"]
            t = state["temp"]
            # dT/dt
            dT = (p * r - (t - self.ambient)) / (r * c) * dt
            # Add noise
            dT += random.uniform(-0.1,0.1)
            state["temp"] += dT

    def get_temps(self):
        return {dev: state["temp"] for dev, state in self.devices.items()}

    def check_threshold(self, t_max: float = 85.0):
        return {dev: temp for dev, temp in self.get_temps().items() if temp > t_max}

    def simulate(self, steps: int = 20):
        print("=== Thermal Model T_i(t) ===")
        print(f"Ambient: {self.ambient}°C")
        for step in range(steps):
            self.update(dt=1.0)
            temps = self.get_temps()
            max_t = max(temps.values())
            avg_t = sum(temps.values())/len(temps)
            print(f"Step {step}: max={max_t:.1f}°C avg={avg_t:.1f}°C temps={ {k: f'{v:.1f}' for k,v in temps.items()} }")
            over = self.check_threshold(85.0)
            if over:
                print(f"  WARNING: Over threshold 85°C: {over}")
            time.sleep(0.1)

if __name__ == "__main__":
    model = ThermalModel()
    model.simulate(20)
