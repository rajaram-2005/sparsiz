"""Deployment — Local AI, Phone Local AI, Data-Center Local AI, high-end models"""
try:
    from .local_ai import LocalAI, ExecutionMode
except ImportError:
    LocalAI = ExecutionMode = None

try:
    from .phone_local_ai import PhoneLocalAI as PhoneLocalAI2, PhoneExecutionMode, PhoneLocalAIRegistry, PhoneModelRouter
except ImportError:
    PhoneLocalAI2 = PhoneExecutionMode = PhoneLocalAIRegistry = PhoneModelRouter = None

try:
    from .datacenter_local_ai import DataCenterLocalAI, DataCenterExecutionMode, DataCenterLocalAIRegistry, DataCenterModelRouter
except ImportError:
    DataCenterLocalAI = DataCenterExecutionMode = DataCenterLocalAIRegistry = DataCenterModelRouter = None

__all__ = ["LocalAI","ExecutionMode","PhoneLocalAI2","PhoneExecutionMode","PhoneLocalAIRegistry","PhoneModelRouter","DataCenterLocalAI","DataCenterExecutionMode","DataCenterLocalAIRegistry","DataCenterModelRouter"]
