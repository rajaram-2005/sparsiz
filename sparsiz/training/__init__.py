"""Training Fabric v0.9.0 — Quantum + Neuromorphic + 13 Autopoietic Frameworks"""
from .dataforge import DataForge, DataSample, QualityEngine, DataQualityTier
from .synthforge import SynthForge, SyntheticSample, SyntheticModality
from .failure_memory import FailureMemory, FailureRecord, FailureCategory, RootCause, RegressionMemory
from .curriculum import CurriculumEngine, CurriculumSample, DifficultyLevel
from .neural_foundry import NeuralFoundry, ModelSpec, ArchitectureType, ModelModality, MoERouter, HardwareAwareRouter
from .rl import RLEngine, RewardComponents, Environment
from .evolution import EvolutionEngine, CandidateChangeType
from .distillation import DistillationEngine, ModelSize
from .evaluation import EvaluationFabric, BenchmarkCategory, RedTeam
try:
    from .quantum_training import QuantumTrainingEngine
    from .neuromorphic_training import NeuromorphicTrainingEngine
except ImportError:
    QuantumTrainingEngine = None
    NeuromorphicTrainingEngine = None

__all__ = [
    "DataForge","DataSample","QualityEngine","DataQualityTier",
    "SynthForge","SyntheticSample","SyntheticModality",
    "FailureMemory","FailureRecord","FailureCategory","RootCause","RegressionMemory",
    "CurriculumEngine","CurriculumSample","DifficultyLevel",
    "NeuralFoundry","ModelSpec","ArchitectureType","ModelModality","MoERouter","HardwareAwareRouter",
    "RLEngine","RewardComponents","Environment",
    "EvolutionEngine","CandidateChangeType",
    "DistillationEngine","ModelSize",
    "EvaluationFabric","BenchmarkCategory","RedTeam",
    "QuantumTrainingEngine","NeuromorphicTrainingEngine",
]
