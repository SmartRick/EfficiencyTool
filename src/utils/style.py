from .config import Config
from PySide6.QtGui import QColor, QLinearGradient, QGradient
from typing import Dict, Any
import logging

class StyleManager:
    """样式管理器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = Config()
            self.initialized = True
            self._setup_logging()
    
    def _setup_logging(self):
        """设置日志"""
        self.logger = logging.getLogger('StyleManager')
        self.logger.setLevel(logging.DEBUG)
    
    def get_style(self, component: str) -> str:
        """获取组件样式
        Args:
            component: 组件名称
        Returns:
            str: 组件样式表
        """
        try:
            template = self.config.get(f'templates.{component}')
            if not template:
                self.logger.warning(f'Style template not found for component: {component}')
                return ''
            
            style_data = self._get_style_data(component)
            if not style_data:
                self.logger.warning(f'Style data not found for component: {component}')
                return ''
            
            return template % style_data
        except KeyError as e:
            self.logger.error(f'Missing key in style data for {component}: {e}')
            return ''
        except Exception as e:
            self.logger.error(f'Error getting style for {component}: {e}')
            return ''
    
    def get_component_config(self, component: str, key: str = None, default = None):
        """获取组件配置
        Args:
            component: 组件名称
            key: 配置键名
            default: 默认值
        Returns:
            Any: 配置值
        """
        try:
            path = f'components.{component}'
            if key:
                path = f'{path}.{key}'
            
            value = self.config.get(path)
            if value is None:
                self.logger.debug(f'Using default value for {path}: {default}')
                return default
            return value
        except Exception as e:
            self.logger.error(f'Error getting component config: {e}')
            return default
    
    def get_global_config(self, key: str, default = None):
        """获取全局配置
        Args:
            key: 配置键名
            default: 默认值
        Returns:
            Any: 配置值
        """
        try:
            value = self.config.get(f'global.{key}')
            if value is None:
                self.logger.debug(f'Using default value for global.{key}: {default}')
                return default
            return value
        except Exception as e:
            self.logger.error(f'Error getting global config: {e}')
            return default
    
    def _get_style_data(self, component: str) -> Dict[str, Any]:
        """获取样式数据"""
        try:
            # 获取全局配置
            global_config = {
                'background': self.get_global_config('colors.background'),
                'border_color': self.get_global_config('colors.border'),
                'border_radius': self.get_global_config('border_radius'),
                'font_size': self.get_global_config('font_size'),
                'text_color': self.get_global_config('colors.text'),
                'font_family': self.get_global_config('font_family'),
            }
            
            # 组件特定的默认配置
            default_configs = {
                'time_button': {
                    'padding': [6, 12],
                    'min_width': 80,
                    'text_color': '#007AFF',
                    'background': 'rgba(0, 122, 255, 0.1)',
                    'hover_background': 'rgba(0, 122, 255, 0.15)',
                    'pressed_background': 'rgba(0, 122, 255, 0.2)',
                },
                'control_panel': {
                    'padding': 20,
                    'spacing': 16,
                    'icon_spacing': 8,
                    'label_color': '#666666',
                },
                'title_bar': {
                    'height': 38,
                    'background': 'transparent',
                }
            }
            
            # 获取组件特定配置
            component_config = self.get_component_config(component, default=default_configs.get(component, {}))
            
            # 合并配置
            style_data = {**global_config, **component_config}
            
            # 验证必要的样式数据
            required_keys = {
                'time_button': {'padding', 'min_width', 'text_color', 'background'},
                'control_panel': {'padding', 'spacing', 'label_color'},
                'title_bar': {'height', 'background'},
            }.get(component, {'background', 'border_radius', 'font_size'})
            
            missing_keys = required_keys - set(style_data.keys())
            if missing_keys:
                self.logger.warning(f'Missing required style data for {component}: {missing_keys}')
            
            return style_data
            
        except Exception as e:
            self.logger.error(f'Error preparing style data for {component}: {e}')
            return {} 