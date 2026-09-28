"""BCI End-to-End Example"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.saram import Saram, SaramConfig
from interfaces.bci.eeg_interface import BCIInterface
from sparsiz.faisanth import Faisanth, TaskDescriptor
from sparsiz.premsoth import Premsoth, AgentOutput

def main():
    print("=== BCI End-to-End ===")
    bci = BCIInterface()
    features = bci.pipeline()
    print(f"BCI features: {features}")

    saram = Saram(SaramConfig(raw_dim=64, latent_dim=16))
    latent, meta = saram.encode({"eeg": features["eeg"]})
    print(f"SARAM latent dim={meta['latent_dim']} compression={meta['compression_ratio']}")

    faisanth = Faisanth()
    task = TaskDescriptor.bci()
    route = faisanth.route(task)
    print(f"FAISANTH route: {route}")

    outputs = [
        AgentOutput("EEGClassifier1","BCI_001",{"label":"left","confidence":0.85},0.85,0.9),
        AgentOutput("EEGClassifier2","BCI_001",{"label":"left","confidence":0.88},0.88,0.92),
        AgentOutput("EEGClassifier3","BCI_001",{"label":"left","confidence":0.82},0.82,0.88),
    ]
    premsoth = Premsoth()
    decision = premsoth.verify("BCI_001", outputs)
    print(f"PREMSOTH verified={decision['verified']} agreement={decision['agreement_score']:.2f}")
    print(f"Never raw BCI → actuators, must go through PREMSOTH safety gate")
    print(f"Direct actuator allowed? {bci.safe_actuator_check(features)} (False)")

if __name__ == "__main__":
    main()
