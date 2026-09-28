"""
Fields — All Fields in the World Skills
v1.0.0-agi-omni-skills

This module re-exports all skills from registry for easy access
"""

from ..registry import SkillRegistry
from ..skill import Skill, SkillDefinition, SkillCapability, SkillCategory, SafetyLevel

# Global registry instance for all fields
_global_registry = None

def get_registry() -> SkillRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = SkillRegistry()
    return _global_registry

def get_all_skills():
    return get_registry().list_all()

def get_fields():
    return get_registry().list_fields()

__all__ = ["get_registry", "get_all_skills", "get_fields", "Skill", "SkillDefinition", "SkillCapability", "SkillCategory", "SafetyLevel"]
