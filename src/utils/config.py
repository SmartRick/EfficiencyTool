import yaml
import os
import logging
from typing import Any, Dict

class Config:
    """配置管理器"""
    _instance = None
    _config: Dict = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._config:
            self._setup_logging()
            self._load_default_config()
            self._load_config()
            self._merge_configs()
    
    def _setup_logging(self):
        """设置日志"""
        self.logger = logging.getLogger('Config')
        self.logger.setLevel(logging.DEBUG)
    
    def _load_config(self):
        """加载配置文件"""
        try:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(current_dir, 'config', 'style.yaml')
            
            self.logger.debug(f'Loading config from: {config_path}')
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
                
            self.logger.debug('Config loaded successfully')
            
        except Exception as e:
            self.logger.error(f'Error loading config: {e}')
            self._config = {}
    
    def _load_default_config(self):
        """加载默认配置"""
        try:
            default_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'config',
                'default.yaml'
            )
            
            self.logger.debug(f'Loading default config from: {default_path}')
            
            with open(default_path, 'r', encoding='utf-8') as f:
                self._default_config = yaml.safe_load(f)
                
            self.logger.debug('Default config loaded successfully')
            
        except Exception as e:
            self.logger.error(f'Error loading default config: {e}')
            self._default_config = {}
    
    def _merge_configs(self):
        """合并默认配置和用户配置"""
        from copy import deepcopy
        
        merged = deepcopy(self._default_config)
        
        def merge_dict(source, destination):
            for key, value in source.items():
                if isinstance(value, dict):
                    node = destination.setdefault(key, {})
                    merge_dict(value, node)
                else:
                    destination[key] = value
            return destination
        
        self._config = merge_dict(self._config, merged)
    
    def get(self, path: str, default: Any = None) -> Any:
        """获取配置值"""
        try:
            value = self._config
            keys = path.split('.')
            
            # 处理嵌套路径
            for key in keys:
                if not isinstance(value, dict):
                    self.logger.debug(f'Invalid path: {path}, value is not a dict')
                    return default
                if key not in value:
                    self.logger.debug(f'Key not found: {key} in path {path}')
                    return default
                value = value[key]
            
            return value
        except Exception as e:
            self.logger.debug(f'Error getting config for path: {path}: {e}')
            return default
    
    def reload(self):
        """重新加载配置"""
        self._config = {}
        self._load_config() 
    
    def set(self, path: str, value: Any) -> None:
        """设置配置值"""
        try:
            keys = path.split('.')
            current = self._config
            
            # 遍历到最后一个键之前
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # 设置最后一个键的值
            current[keys[-1]] = value
            
            # 保存到文件
            self._save_config()
            
        except Exception as e:
            self.logger.error(f'Error setting config for path {path}: {e}')
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'config',
                'style.yaml'
            )
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, allow_unicode=True)
                
            self.logger.debug('Config saved successfully')
            
        except Exception as e:
            self.logger.error(f'Error saving config: {e}') 