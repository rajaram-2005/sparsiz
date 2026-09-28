"""
SARAM Decoder g_φ(z): R^{d_z} → R^{d_r}
"""

from dataclasses import dataclass
from typing import List
import math
import random

@dataclass
class DecoderConfig:
    latent_dim: int = 128
    raw_dim: int = 1024

class Decoder:
    def __init__(self, config: DecoderConfig):
        self.config = config
        self.weights = [[random.uniform(-0.1,0.1) for _ in range(config.latent_dim)] for _ in range(config.raw_dim)]

    def decode(self, z: List[float]) -> List[float]:
        # x̂ = g_φ(z)
        x_hat = []
        for i in range(self.config.raw_dim):
            s = sum(w*zi for w,zi in zip(self.weights[i], z))
            x_hat.append(s)
        return x_hat
