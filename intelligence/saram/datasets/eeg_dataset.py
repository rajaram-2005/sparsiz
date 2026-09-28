"""
Offline EEG dataset for Phase 7 BCI
Start with offline EEG dataset → real-time EEG → SARAM streaming → real-time inference
Do not start with invasive neural interfaces
"""

import random
from typing import List, Dict

class EEGDataset:
    def __init__(self, channels: int = 64, samples: int = 256):
        self.channels = channels
        self.samples = samples

    def load_offline(self) -> List[Dict]:
        # Simulate offline EEG dataset
        dataset = []
        for i in range(100):
            eeg = [random.gauss(0,1) for _ in range(self.channels)]
            label = random.choice(["left","right","rest"])
            dataset.append({"eeg": eeg, "label": label, "id": f"EEG_{i}"})
        return dataset

    def stream_realtime(self):
        # Simulate real-time EEG streaming
        while True:
            eeg = [random.gauss(0,1) for _ in range(self.channels)]
            yield {"eeg": eeg, "timestamp": 0}

if __name__ == "__main__":
    ds = EEGDataset()
    data = ds.load_offline()
    print(f"Loaded {len(data)} offline EEG samples")
    print(f"Sample: {data[0]['label']}, eeg mean={sum(data[0]['eeg'])/len(data[0]['eeg']):.2f}")
