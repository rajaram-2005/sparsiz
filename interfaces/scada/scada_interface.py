"""
Industrial SCADA Integration
Recommended: PLC → Modbus TCP/OPC UA/MQTT gateway → SARAM → FAISANTH → AI agents → PREMSOTH → Safety layer → PLC/HMI
Keep deterministic control logic independent from AI
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import random

@dataclass
class PLCTelemetry:
    voltage: float
    current: float
    temperature: float
    pressure: float
    vibration: float
    rpm: float
    power: float
    harmonics: float

class ModbusGateway:
    def read_plc(self) -> PLCTelemetry:
        # Simulate Modbus TCP reading
        return PLCTelemetry(
            voltage=400+random.uniform(-10,10),
            current=14.2+random.uniform(-1,1),
            temperature=81+random.uniform(-5,5),
            pressure=5.0,
            vibration=8.3+random.uniform(-1,1),
            rpm=1480+random.uniform(-20,20),
            power=400*14.2,
            harmonics=0.05,
        )

class OPCUAGateway:
    def read_plc(self) -> PLCTelemetry:
        # Simulate OPC UA
        return ModbusGateway().read_plc()

class MQTTGateway:
    def read_plc(self) -> PLCTelemetry:
        # Simulate MQTT
        return ModbusGateway().read_plc()

class SafetyLayer:
    """
    Safety layer: AI recommendation → PREMSOTH → Safety policy engine → Range checking → Interlock checking → Human/authorized controller → PLC
    Vmin≤Vcmd≤Vmax, Icmd≤Imax, T<Tcritical
    """
    def __init__(self):
        self.v_min = 0
        self.v_max = 480
        self.i_max = 100
        self.t_critical = 150

    def check(self, command: Dict[str, Any]) -> bool:
        if "voltage" in command:
            if not (self.v_min <= command["voltage"] <= self.v_max):
                return False
        if "current" in command:
            if command["current"] > self.i_max:
                return False
        if "temperature" in command:
            if command["temperature"] >= self.t_critical:
                return False
        return True

    def interlock_check(self, command: Dict[str, Any]) -> bool:
        # Independent deterministic logic
        if command.get("guard_open"):
            return False
        return True

class SCADAInterface:
    def __init__(self):
        self.modbus = ModbusGateway()
        self.opcua = OPCUAGateway()
        self.mqtt = MQTTGateway()
        self.safety = SafetyLayer()

    def pipeline(self, gateway: str = "modbus"):
        """
        PLC → Gateway → SARAM → FAISANTH → AI agents → PREMSOTH → Safety layer → PLC/HMI
        """
        if gateway=="modbus":
            telemetry = self.modbus.read_plc()
        elif gateway=="opcua":
            telemetry = self.opcua.read_plc()
        else:
            telemetry = self.mqtt.read_plc()

        print(f"PLC telemetry: V={telemetry.voltage:.1f}V I={telemetry.current:.1f}A T={telemetry.temperature:.1f}°C vibration={telemetry.vibration:.1f}mm/s RPM={telemetry.rpm:.0f}")

        # SARAM would process here
        saram_features = {
            "voltage": telemetry.voltage,
            "current": telemetry.current,
            "temperature": telemetry.temperature,
            "vibration": telemetry.vibration,
            "rpm": telemetry.rpm,
            "power": telemetry.power,
        }

        # FAISANTH routing, AI agents, PREMSOTH verification would happen

        # Safety layer before PLC command
        command = {"voltage": telemetry.voltage, "current": telemetry.current, "temperature": telemetry.temperature}
        if self.safety.check(command) and self.safety.interlock_check(command):
            print(f"Safety check passed: {command}")
            print("Authorized to send to PLC/HMI")
            return True
        else:
            print(f"Safety check FAILED: {command}, blocking PLC command")
            return False

if __name__ == "__main__":
    scada = SCADAInterface()
    scada.pipeline("modbus")
    scada.pipeline("opcua")
    scada.pipeline("mqtt")

    # Test safety failure
    print("\n--- Safety Failure Test ---")
    bad_command = {"voltage": 600, "current": 14, "temperature": 81}
    print(f"Command {bad_command} safety check: {scada.safety.check(bad_command)} (should be False, V out of range)")
