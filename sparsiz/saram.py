"""
SARAM — Semantic Representation / Data Processing
RAW DATA → Filtering → Feature extraction → Encoder f_θ → LATENT VECTOR z (d_z<<d_r) → FAISANTH

Input: x∈R^{d_r}, Encoder: z=f_θ(x), z∈R^{d_z}, d_z<<d_r, Decoder: x̂=g_φ(z)
Training: L = L_rec + λ1 L_physics + λ2 L_task + λ3 L_reg

Data types:
- BCI: EEG/ECoG/neural spikes/biopotential
- Industrial: voltage/current/temperature/pressure/vibration/RPM/power/harmonics/PLC
- AI: tokens/embeddings/sensor embeddings/multimodal

Physics: P=VI, S=P+jQ, P_mech=Tω, mẍ+cẋ+kx=F(t)
Encoder trained so latent retains info necessary for physical relationships.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import math
import random

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

@dataclass
class SaramConfig:
    raw_dim: int = 1024
    latent_dim: int = 128
    encoder_type: str = "physics_autoencoder"
    lambda_physics: float = 0.5
    lambda_task: float = 0.3
    lambda_reg: float = 0.1

class PhysicsConstraints:
    """
    Physics constraints for loss:
    P=VI, S=P+jQ, P_mech=Tω, mẍ+cẋ+kx=F(t)
    """

    @staticmethod
    def power_vi(v: float, i: float) -> float:
        # P=VI
        return v * i

    @staticmethod
    def apparent_power(p: float, q: float) -> complex:
        # S=P+jQ
        return complex(p, q)

    @staticmethod
    def mechanical_power(torque: float, omega: float) -> float:
        # P_mech = Tω
        return torque * omega

    @staticmethod
    def vibration(m: float, c: float, k: float, x: float, x_dot: float, x_ddot: float) -> float:
        # mẍ + cẋ + kx = F(t) → return F(t)
        return m * x_ddot + c * x_dot + k * x

    @staticmethod
    def check_consistency(sample: Dict[str, float]) -> float:
        """
        Return physics consistency score 0..1
        Encoder should retain info for these relationships
        """
        score = 1.0
        # Check P=VI
        if "voltage" in sample and "current" in sample and "power" in sample:
            p_expected = sample["voltage"] * sample["current"]
            p_actual = sample["power"]
            if abs(p_expected) > 1e-6:
                err = abs(p_expected - p_actual) / abs(p_expected)
                score *= max(0.0, 1.0 - err)

        # Check P_mech=Tω
        if "torque" in sample and "omega" in sample and "mech_power" in sample:
            p_expected = sample["torque"] * sample["omega"]
            err = abs(p_expected - sample["mech_power"]) / (abs(p_expected)+1e-6)
            score *= max(0.0, 1.0 - err)

        # Check temperature plausible
        if "temperature" in sample:
            if sample["temperature"] > 200 or sample["temperature"] < -50:
                score *= 0.1

        return score

if HAS_TORCH:
    class PhysicsAutoencoder(nn.Module):
        """
        Encoder: z=f_θ(x), Decoder: x̂=g_φ(z)
        Loss: L = L_rec + λ1 L_physics + λ2 L_task + λ3 L_reg
        """
        def __init__(self, config: SaramConfig):
            super().__init__()
            self.config = config
            self.encoder = nn.Sequential(
                nn.Linear(config.raw_dim, 512),
                nn.ReLU(),
                nn.Linear(512, 256),
                nn.ReLU(),
                nn.Linear(256, config.latent_dim),
            )
            self.decoder = nn.Sequential(
                nn.Linear(config.latent_dim, 256),
                nn.ReLU(),
                nn.Linear(256, 512),
                nn.ReLU(),
                nn.Linear(512, config.raw_dim),
            )

        def forward(self, x):
            z = self.encoder(x)  # f_θ(x)
            x_hat = self.decoder(z)  # g_φ(z)
            return z, x_hat

        def loss(self, x, x_hat, z, physics_sample=None, task_label=None):
            # L_rec
            l_rec = nn.MSELoss()(x_hat, x)
            # L_physics
            l_physics = 0.0
            if physics_sample:
                # Encourage latent to retain physics info: dummy loss
                l_physics = torch.mean(z**2) * 0.01
            # L_task (if supervised)
            l_task = 0.0
            # L_reg
            l_reg = torch.mean(z**2)

            total = l_rec + self.config.lambda_physics * l_physics + self.config.lambda_task * l_task + self.config.lambda_reg * l_reg
            return total, {"rec": l_rec.item(), "physics": l_physics if isinstance(l_physics,float) else l_physics.item() if hasattr(l_physics,'item') else 0, "reg": l_reg.item()}
else:
    class PhysicsAutoencoder:
        def __init__(self, config: SaramConfig):
            self.config = config
            print("Torch not available, using numpy mock encoder")

        def encode(self, x):
            # Mock: random projection d_r -> d_z, d_z << d_r
            import numpy as np
            x = np.array(x)
            # Simple compression: average pooling + linear
            # CompressionRatio = d_raw / d_latent
            latent = np.mean(x.reshape(-1, x.shape[-1] // self.config.latent_dim), axis=1) if len(x.shape)>0 else x[:self.config.latent_dim]
            return latent

        def decode(self, z):
            import numpy as np
            # Mock reconstruction
            return np.tile(z, int(self.config.raw_dim // self.config.latent_dim +1))[:self.config.raw_dim]

class Saram:
    def __init__(self, config: Optional[SaramConfig] = None):
        self.config = config or SaramConfig()
        self.physics = PhysicsConstraints()
        if HAS_TORCH:
            self.model = PhysicsAutoencoder(self.config)
        else:
            self.model = PhysicsAutoencoder(self.config)
        self.input_rate = 0
        self.compression_ratio = self.config.raw_dim / self.config.latent_dim

    def preprocess(self, raw_data: Dict[str, Any]) -> List[float]:
        """
        Filtering → Feature extraction
        Supports BCI (EEG/ECoG/spikes/biopotential), Industrial (V/I/T/P/vibration/RPM/power/harmonics/PLC), AI (tokens/embeddings)
        """
        # Example: extract features from motor telemetry
        features = []
        # Industrial
        for key in ["voltage","current","temperature","pressure","vibration","rpm","power","harmonics"]:
            if key in raw_data:
                features.append(float(raw_data[key]))
        # BCI
        if "eeg" in raw_data:
            eeg = raw_data["eeg"]
            if isinstance(eeg, list):
                # Simple feature: mean, std, band power mock
                mean = sum(eeg)/len(eeg) if eeg else 0
                features.extend([mean, 0.1, 0.2])  # mock band powers
        # Pad/truncate to raw_dim
        while len(features) < self.config.raw_dim:
            features.append(0.0)
        return features[:self.config.raw_dim]

    def encode(self, raw_data: Dict[str, Any]) -> Tuple[List[float], Dict]:
        """
        RAW DATA → Filtering → Feature extraction → Encoder → LATENT VECTOR
        """
        x = self.preprocess(raw_data)
        self.input_rate += 1

        if HAS_TORCH:
            import torch
            x_t = torch.tensor(x, dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                z, x_hat = self.model(x_t)
            latent = z.squeeze(0).tolist()
            reconstructed = x_hat.squeeze(0).tolist()
            # Calculate reconstruction error
            rec_error = sum((a-b)**2 for a,b in zip(x, reconstructed)) / len(x)
        else:
            latent = self.model.encode(x).tolist() if hasattr(self.model.encode(x), 'tolist') else list(self.model.encode(x))
            reconstructed = self.model.decode(latent)
            rec_error = 0.01  # mock

        physics_score = self.physics.check_consistency(raw_data)

        return latent, {
            "compression_ratio": self.compression_ratio,
            "reconstruction_error": rec_error,
            "physics_consistency": physics_score,
            "input_rate": self.input_rate,
            "latent_dim": len(latent),
            "raw_dim": len(x),
        }

    def decode(self, latent: List[float]) -> List[float]:
        if HAS_TORCH:
            import torch
            z_t = torch.tensor(latent, dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                x_hat = self.model.decoder(z_t)
            return x_hat.squeeze(0).tolist()
        else:
            return self.model.decode(latent).tolist()

    def stream(self, data_stream):
        """
        POST /stream — streaming SARAM
        """
        for raw in data_stream:
            latent, meta = self.encode(raw)
            yield latent, meta

# Example datasets
class IndustrialDataset:
    @staticmethod
    def motor_example():
        return {
            "vibration": 8.3,  # mm/s
            "current": 14.2,   # A
            "temperature": 81, # °C
            "rpm": 1480,
            "voltage": 400,
            "power": 400*14.2, # P=VI
            "torque": 50,
            "omega": 155, # rad/s ~1480 RPM
            "mech_power": 50*155, # Tω
        }

    @staticmethod
    def bearing_fault():
        return {
            "vibration": 12.5,
            "current": 16.0,
            "temperature": 95,
            "rpm": 1450,
            "voltage": 400,
            "power": 6400,
        }

class BCIDataset:
    @staticmethod
    def eeg_example():
        # Simulated EEG 64 channels, 256 samples
        return {
            "eeg": [random.gauss(0,1) for _ in range(64)],
            "sampling_rate": 256,
        }

if __name__ == "__main__":
    saram = Saram(SaramConfig(raw_dim=128, latent_dim=16))
    raw = IndustrialDataset.motor_example()
    latent, meta = saram.encode(raw)
    print(f"Compressed {meta['raw_dim']} -> {meta['latent_dim']}, ratio={meta['compression_ratio']:.1f}, rec_err={meta['reconstruction_error']:.4f}, physics={meta['physics_consistency']:.2f}")
