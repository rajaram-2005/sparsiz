"""
Industrial telemetry dataset: voltage, current, temperature, pressure, vibration, RPM, power, harmonics, PLC telemetry
"""

import random
from typing import List, Dict

class IndustrialDataset:
    @staticmethod
    def motor_normal() -> Dict:
        return {
            "voltage": 400 + random.uniform(-5,5),
            "current": 14.2 + random.uniform(-0.5,0.5),
            "temperature": 70 + random.uniform(-5,5),
            "pressure": 5.0,
            "vibration": 4.5 + random.uniform(-1,1),
            "rpm": 1480 + random.uniform(-10,10),
            "power": 400*14.2,
            "harmonics": 0.03,
            "label": "normal",
        }

    @staticmethod
    def motor_bearing_fault() -> Dict:
        return {
            "voltage": 400 + random.uniform(-5,5),
            "current": 16.0 + random.uniform(-1,1),
            "temperature": 85 + random.uniform(-5,10),
            "pressure": 5.0,
            "vibration": 8.3 + random.uniform(-1,2),
            "rpm": 1450 + random.uniform(-20,20),
            "power": 400*16.0,
            "harmonics": 0.08,
            "label": "bearing_fault",
        }

    @staticmethod
    def generate(n: int = 1000) -> List[Dict]:
        data = []
        for i in range(n):
            if random.random() < 0.7:
                data.append(IndustrialDataset.motor_normal())
            else:
                data.append(IndustrialDataset.motor_bearing_fault())
        return data

if __name__ == "__main__":
    data = IndustrialDataset.generate(10)
    for d in data:
        print(d)
