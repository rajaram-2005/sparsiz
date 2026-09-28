"""Deployment — Local AI, Phone Local AI, online + local for phones"""
try:
    from .local_ai import LocalAI, ExecutionMode
except ImportError:
    LocalAI = ExecutionMode = None

try:
    from .phone_local_ai import PhoneLocalAI as PhoneLocalAI2, PhoneExecutionMode, PhoneLocalAIRegistry, PhoneModelRouter
except ImportError:
    PhoneLocalAI2 = PhoneExecutionMode = PhoneLocalAIRegistry = PhoneModelRouter = None

__all__ = ["LocalAI","ExecutionMode","PhoneLocalAI2","PhoneExecutionMode","PhoneLocalAIRegistry","PhoneModelRouter"]
