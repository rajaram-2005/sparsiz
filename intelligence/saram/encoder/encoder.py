"""
SARAM Encoder f_θ(x): R^{d_r} → R^{d_z}, d_z << d_r
"""
from dataclasses import dataclass
from typing import List
import math
import random

@dataclass
class EncoderConfig:
    raw_dim: int = 1024
    latent_dim: int = 128
    hidden: List[int] = None

    def __post_init__(self):
        if self.hidden is None:
            self.hidden = [512,256]

class PhysicsGuidedEncoder:
    """
    Encoder trained so latent retains info necessary for physical relationships
    P=VI, S=P+jQ, P_mech=Tω, mẍ+cẋ+kx=F(t)
    """
    def __init__(self, config: EncoderConfig):
        self.config = config
        # Mock weights for prototype without torch
        self.weights = [[random.uniform(-0.1,0.1) for _ in range(config.raw_dim)] for _ in range(config.latent_dim)]

    def encode(self, x: List[float]) -> List[float]:
        # Simple linear projection + tanh: z = f_θ(x)
        z = []
        for i in range(self.config.latent_dim):
            s = sum(w*xi for w,xi in zip(self.weights[i], x[:self.config.raw_dim]))
            z.append(math.tanh(s))
        return z

    def compression_ratio(self) -> float:
        return self.config.raw_dim / self.config.latent_dim
