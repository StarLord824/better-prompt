"""
Plugin system foundation for extensibility.
"""

from .registry import PluginRegistry
from .manifest import PluginManifest, PluginType

__all__ = ["PluginRegistry", "PluginManifest", "PluginType"]
