"""
Neuromorphic AGI E2E — Unbelievable Patent v0.9.0
Demonstrates Neuromorphic AGI with LIF+STDP, SNN [128,64,32,16], always-on wake-up
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.neuromorphic.neuromorphic_agi import NeuromorphicAGI
from sparsiz.training.neuromorphic_training import NeuromorphicTrainingEngine
from sparsiz.hal import HAL

def main():
    print("="*100)
    print("Neuromorphic AGI E2E — LIF+STDP SNN Low-Power Always-On")
    print("="*100)

    hal = HAL()
    neuro_device = hal.select_device("NEURO-1")
    print(f"\nNeuromorphic device: {neuro_device.device_id() if neuro_device else 'Not found'} capabilities: {neuro_device.capabilities() if neuro_device else 'N/A'}")

    # Training
    print("\n### Neuromorphic Training ===")
    nt_engine = NeuromorphicTrainingEngine()
    nt_engine.train_full(data_size=500)

    # Neuromorphic AGI
    print("\n### Neuromorphic AGI Inference ===")
    nagi = NeuromorphicAGI()
    nagi.train_snn(n_samples=100)

    # Test cases: different event streams
    test_cases = [
        ([{"type": "motion", "timestamp": i*10} for i in range(10)] + [{"type": "sound", "timestamp": 50}], "Motion + sound"),
        ([{"type": "idle", "timestamp": i*5} for i in range(5)], "Idle"),
        ([{"type": "anomaly", "timestamp": i*2} for i in range(20)], "Anomaly — should wake-up ANN"),
        ([{"type": "wake_word", "timestamp": 10}, {"type": "gesture", "timestamp": 20}], "Wake word + gesture — should wake-up ANN"),
        ([{"type": "motion", "timestamp": i} for i in range(100)], "High event rate motion"),
    ]

    for events, desc in test_cases:
        print(f"\n--- Test: {desc} — {len(events)} events ---")
        result = nagi.hybrid_inference(events)
        print(f"Result: class={result['event_class']} conf={result['confidence']:.3f} power={result['power_mw']:.2f}mW wake_up={result['wake_up_ann']}")

    # Power budget
    print("\n### Power Budget ===")
    print("Neuromorphic: 10mW base + 0.01mW per spike, budget 100mW")
    print("Always-on low-power monitor, ANN wake-up only when needed")
    print("Event-driven SNN, not clock-driven, ultra low-power")

    # Final
    print("\n" + "="*100)
    print("Neuromorphic AGI E2E Complete")
    print("Patentable: LIF tau_m dv/dt = -(v-v_rest)+R_m I, STDP LTP/LTD, SNN [128,64,32,16], always-on wake-up, ANN→SNN→STDP→Hybrid")
    print("Safety: Low-power always-on, PREMSOTH gate, no direct actuator without verification")
    print("="*100)

if __name__ == "__main__":
    main()
