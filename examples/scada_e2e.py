"""SCADA End-to-End Example"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from interfaces.scada.scada_interface import SCADAInterface

def main():
    print("=== SCADA End-to-End ===")
    scada = SCADAInterface()
    for gw in ["modbus","opcua","mqtt"]:
        print(f"\n--- Gateway: {gw} ---")
        scada.pipeline(gw)

if __name__ == "__main__":
    main()
