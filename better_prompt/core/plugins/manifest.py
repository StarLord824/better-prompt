"""
Plugin Manifest Module

This module handles plugin manifest loading and validation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path
import json
from enum import Enum


class PluginType(Enum):
    """Types of plugins supported."""
    
    CLASSIFIER = "classifier"
    FORMATTER = "formatter"
    REFINER = "refiner"
    LLM_PROVIDER = "llm_provider"
    VALIDATOR = "validator"
    CUSTOM = "custom"


@dataclass
class PluginManifest:
    """
    Plugin manifest containing metadata and configuration.
    
    Attributes:
        name: Plugin name
        version: Plugin version
        plugin_type: Type of plugin
        description: Plugin description
        author: Plugin author
        entry_point: Entry point module/class
        dependencies: List of required dependencies
        config: Plugin-specific configuration
        enabled: Whether the plugin is enabled
    """
    
    name: str
    version: str
    plugin_type: PluginType
    description: str
    author: str
    entry_point: str
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, any] = field(default_factory=dict)
    enabled: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict) -> "PluginManifest":
        """
        Create a PluginManifest from a dictionary.
        
        Args:
            data: Dictionary containing manifest data
            
        Returns:
            PluginManifest instance
        """
        # Convert plugin_type string to enum
        plugin_type_str = data.get("plugin_type", "custom")
        try:
            plugin_type = PluginType(plugin_type_str.lower())
        except ValueError:
            plugin_type = PluginType.CUSTOM
        
        return cls(
            name=data["name"],
            version=data["version"],
            plugin_type=plugin_type,
            description=data.get("description", ""),
            author=data.get("author", "Unknown"),
            entry_point=data["entry_point"],
            dependencies=data.get("dependencies", []),
            config=data.get("config", {}),
            enabled=data.get("enabled", True)
        )
    
    @classmethod
    def from_file(cls, manifest_path: Path) -> "PluginManifest":
        """
        Load a plugin manifest from a JSON file.
        
        Args:
            manifest_path: Path to the manifest file
            
        Returns:
            PluginManifest instance
        """
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict:
        """
        Convert manifest to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "version": self.version,
            "plugin_type": self.plugin_type.value,
            "description": self.description,
            "author": self.author,
            "entry_point": self.entry_point,
            "dependencies": self.dependencies,
            "config": self.config,
            "enabled": self.enabled
        }
    
    def save(self, manifest_path: Path) -> None:
        """
        Save the manifest to a JSON file.
        
        Args:
            manifest_path: Path where to save the manifest
        """
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def validate(self) -> List[str]:
        """
        Validate the manifest for completeness and correctness.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not self.name:
            errors.append("Plugin name is required")
        
        if not self.version:
            errors.append("Plugin version is required")
        
        if not self.entry_point:
            errors.append("Entry point is required")
        
        # Validate version format (simple check)
        if self.version and not self._is_valid_version(self.version):
            errors.append(f"Invalid version format: {self.version}")
        
        return errors
    
    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """
        Check if version string is valid (simple semver check).
        
        Args:
            version: Version string
            
        Returns:
            True if valid, False otherwise
        """
        parts = version.split('.')
        if len(parts) < 2 or len(parts) > 3:
            return False
        
        try:
            for part in parts:
                int(part)
            return True
        except ValueError:
            return False
    
    def __str__(self) -> str:
        """String representation of the manifest."""
        status = "enabled" if self.enabled else "disabled"
        return f"{self.name} v{self.version} ({self.plugin_type.value}) - {status}"


def create_sample_manifest(
    name: str,
    plugin_type: PluginType,
    entry_point: str,
    output_path: Optional[Path] = None
) -> PluginManifest:
    """
    Create a sample plugin manifest.
    
    Args:
        name: Plugin name
        plugin_type: Type of plugin
        entry_point: Entry point module/class
        output_path: Optional path to save the manifest
        
    Returns:
        PluginManifest instance
    """
    manifest = PluginManifest(
        name=name,
        version="0.1.0",
        plugin_type=plugin_type,
        description=f"Sample {plugin_type.value} plugin",
        author="Better Prompt Team",
        entry_point=entry_point,
        dependencies=[],
        config={},
        enabled=True
    )
    
    if output_path:
        manifest.save(output_path)
    
    return manifest
