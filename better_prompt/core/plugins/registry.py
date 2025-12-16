"""
Plugin Registry Module

This module manages plugin discovery, loading, and lifecycle.
"""

from typing import Dict, List, Optional, Type
from pathlib import Path
import importlib.util
import sys

from .manifest import PluginManifest, PluginType


class PluginRegistry:
    """
    Central registry for managing plugins.
    
    The registry handles plugin discovery, loading, and lifecycle management.
    """
    
    def __init__(self, plugin_directories: Optional[List[Path]] = None):
        """
        Initialize the plugin registry.
        
        Args:
            plugin_directories: List of directories to search for plugins
        """
        self.plugin_directories = plugin_directories or []
        self._plugins: Dict[str, PluginManifest] = {}
        self._loaded_modules: Dict[str, any] = {}
        self._instances: Dict[str, any] = {}
    
    def add_plugin_directory(self, directory: Path) -> None:
        """
        Add a directory to search for plugins.
        
        Args:
            directory: Path to plugin directory
        """
        if directory not in self.plugin_directories:
            self.plugin_directories.append(directory)
    
    def discover_plugins(self) -> int:
        """
        Discover all plugins in the registered directories.
        
        Returns:
            Number of plugins discovered
        """
        discovered_count = 0
        
        for directory in self.plugin_directories:
            if not directory.exists():
                continue
            
            # Look for manifest.json files
            for manifest_path in directory.rglob("manifest.json"):
                try:
                    manifest = PluginManifest.from_file(manifest_path)
                    
                    # Validate manifest
                    errors = manifest.validate()
                    if errors:
                        print(f"Warning: Invalid manifest at {manifest_path}: {errors}")
                        continue
                    
                    # Register the plugin
                    self._plugins[manifest.name] = manifest
                    discovered_count += 1
                    
                except Exception as e:
                    print(f"Error loading manifest from {manifest_path}: {e}")
        
        return discovered_count
    
    def register_plugin(self, manifest: PluginManifest) -> None:
        """
        Manually register a plugin.
        
        Args:
            manifest: Plugin manifest
        """
        errors = manifest.validate()
        if errors:
            raise ValueError(f"Invalid plugin manifest: {errors}")
        
        self._plugins[manifest.name] = manifest
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin.
        
        Args:
            plugin_name: Name of the plugin to unregister
            
        Returns:
            True if plugin was unregistered, False if not found
        """
        if plugin_name in self._plugins:
            # Clean up loaded module and instance
            if plugin_name in self._loaded_modules:
                del self._loaded_modules[plugin_name]
            if plugin_name in self._instances:
                del self._instances[plugin_name]
            
            del self._plugins[plugin_name]
            return True
        
        return False
    
    def load_plugin(self, plugin_name: str) -> any:
        """
        Load a plugin module.
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            Loaded plugin module
        """
        if plugin_name not in self._plugins:
            raise ValueError(f"Plugin not found: {plugin_name}")
        
        # Return cached module if already loaded
        if plugin_name in self._loaded_modules:
            return self._loaded_modules[plugin_name]
        
        manifest = self._plugins[plugin_name]
        
        if not manifest.enabled:
            raise RuntimeError(f"Plugin is disabled: {plugin_name}")
        
        # TODO: Check dependencies
        # For now, we'll skip dependency checking
        
        # Load the module
        try:
            # Parse entry point (format: "module.path:ClassName")
            if ":" in manifest.entry_point:
                module_path, class_name = manifest.entry_point.split(":")
            else:
                module_path = manifest.entry_point
                class_name = None
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the class if specified
            if class_name:
                plugin_class = getattr(module, class_name)
                self._loaded_modules[plugin_name] = plugin_class
            else:
                self._loaded_modules[plugin_name] = module
            
            return self._loaded_modules[plugin_name]
            
        except Exception as e:
            raise RuntimeError(f"Failed to load plugin {plugin_name}: {e}")
    
    def get_plugin_instance(self, plugin_name: str, **kwargs) -> any:
        """
        Get or create a plugin instance.
        
        Args:
            plugin_name: Name of the plugin
            **kwargs: Arguments to pass to plugin constructor
            
        Returns:
            Plugin instance
        """
        # Return cached instance if exists
        if plugin_name in self._instances:
            return self._instances[plugin_name]
        
        # Load the plugin
        plugin_class = self.load_plugin(plugin_name)
        
        # Create instance
        manifest = self._plugins[plugin_name]
        config = {**manifest.config, **kwargs}
        
        try:
            instance = plugin_class(**config)
            self._instances[plugin_name] = instance
            return instance
        except Exception as e:
            raise RuntimeError(f"Failed to instantiate plugin {plugin_name}: {e}")
    
    def list_plugins(
        self,
        plugin_type: Optional[PluginType] = None,
        enabled_only: bool = False
    ) -> List[PluginManifest]:
        """
        List registered plugins.
        
        Args:
            plugin_type: Filter by plugin type
            enabled_only: Only return enabled plugins
            
        Returns:
            List of plugin manifests
        """
        plugins = list(self._plugins.values())
        
        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]
        
        if enabled_only:
            plugins = [p for p in plugins if p.enabled]
        
        return plugins
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginManifest]:
        """
        Get a plugin manifest by name.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            PluginManifest or None if not found
        """
        return self._plugins.get(plugin_name)
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            True if plugin was enabled, False if not found
        """
        if plugin_name in self._plugins:
            self._plugins[plugin_name].enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            True if plugin was disabled, False if not found
        """
        if plugin_name in self._plugins:
            self._plugins[plugin_name].enabled = False
            
            # Clean up loaded instance
            if plugin_name in self._instances:
                del self._instances[plugin_name]
            
            return True
        return False
    
    def get_statistics(self) -> Dict:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_plugins = len(self._plugins)
        enabled_plugins = sum(1 for p in self._plugins.values() if p.enabled)
        loaded_plugins = len(self._loaded_modules)
        
        # Count by type
        by_type = {}
        for plugin in self._plugins.values():
            plugin_type = plugin.plugin_type.value
            by_type[plugin_type] = by_type.get(plugin_type, 0) + 1
        
        return {
            "total_plugins": total_plugins,
            "enabled_plugins": enabled_plugins,
            "disabled_plugins": total_plugins - enabled_plugins,
            "loaded_plugins": loaded_plugins,
            "by_type": by_type
        }
    
    def clear(self) -> None:
        """Clear all plugins from the registry."""
        self._plugins.clear()
        self._loaded_modules.clear()
        self._instances.clear()


# Global registry instance
_global_registry = PluginRegistry()


def get_global_registry() -> PluginRegistry:
    """
    Get the global plugin registry instance.
    
    Returns:
        Global PluginRegistry instance
    """
    return _global_registry
