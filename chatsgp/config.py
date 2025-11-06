"""Configuration management for Chat-SGP"""
import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for Chat-SGP system"""
    
    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to config file (YAML or JSON). 
                        If None, looks for config.yaml or config.json in project root.
            config_dict: Optional dictionary to use as configuration directly.
                        If provided, config_path is ignored.
        """
        self.config_path = config_path
        self.config = config_dict if config_dict is not None else self._load_config()
        self._apply_config()
    
    def _find_config_file(self) -> Optional[Path]:
        """Find config file in project root"""
        project_root = Path(__file__).parent.parent
        possible_paths = [
            project_root / 'config.yaml',
            project_root / 'config.yml',
            project_root / 'config.json',
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        return None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path:
            config_file = Path(self.config_path)
        else:
            config_file = self._find_config_file()
        
        if not config_file or not config_file.exists():
            return self._default_config()
        
        try:
            if config_file.suffix in ['.yaml', '.yml']:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            elif config_file.suffix == '.json':
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._default_config()
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'battery': {
                'capacity_kwh': 5.0,
                'efficiency': 0.95,
                'max_power': 2.0,
                'initial_soc': 0.5
            },
            'prices': {
                'import': 0.25,  # EUR/kWh
                'export': 0.10   # EUR/kWh
            },
            'llm': {
                'model': 'gpt-4o-mini',
                'temperature': 0.0,
                'max_tokens': 300
            },
            'optimization': {
                'default_solver': 'pulp',
                'hours': 24
            },
            'pv_profile': None,  # None means use default
            'load_profile': None  # None means use default
        }
    
    def _apply_config(self):
        """Apply configuration to environment"""
        # Set LLM model if specified
        if 'llm' in self.config and 'model' in self.config['llm']:
            os.environ.setdefault('LLM_MODEL', self.config['llm']['model'])
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'battery.capacity_kwh')"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_battery_config(self) -> Dict[str, Any]:
        """Get battery configuration"""
        return self.config.get('battery', {})
    
    def get_price_config(self) -> Dict[str, Any]:
        """Get price configuration"""
        return self.config.get('prices', {})
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return self.config.get('llm', {})
    
    def get_optimization_config(self) -> Dict[str, Any]:
        """Get optimization configuration"""
        return self.config.get('optimization', {})


# Global config instance
_config_instance: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance

