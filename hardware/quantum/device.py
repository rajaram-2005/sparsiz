"""Quantum Device — optional external accelerator, not assumed inside system
Task classifier → Is problem quantum-suitable? NO→CPU/GPU, YES→Quantum backend
Research targets: combinatorial optimization, QUBO, scheduling, sampling, quantum chemistry
FAISANTH selects quantum only when problem formulation and backend justify
"""
from sparsiz.hal import QuantumDevice
__all__ = ["QuantumDevice"]
