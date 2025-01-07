from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication
from datetime import datetime, timedelta
from .screen_saver import ScreenSaver
from .warning_window import WarningWindow
from utils.config import Config

class ScreenSaverManager(QObject):
    """
    屏保管理器
    负责管理定时器、展示警告、控制屏保
    """
    break_started = Signal()
    break_finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.screen_saver = None
        self.warning_window = None
        
        # 初始化定时器
        self.work_timer = QTimer(self)
        self.break_timer = QTimer(self)
        self.warning_timer = QTimer(self)
        
        self.setup_timers()
        self.setup_connections()
        
    def setup_timers(self):
        """设置定时器"""
        work_mins = self.config.get("screensaver.work_duration")
        self.work_timer.setInterval(work_mins * 60 * 1000)  # 转换为毫秒
        self.work_timer.start()
        
    def setup_connections(self):
        """设置信号连接"""
        self.work_timer.timeout.connect(self.prepare_break)
        self.warning_timer.timeout.connect(self.start_break)
        self.break_timer.timeout.connect(self.finish_break)
        
    def prepare_break(self):
        """准备休息,显示警告窗口"""
        warning_secs = self.config.get("screensaver.warning_time")
        self.warning_window = WarningWindow(warning_secs)
        self.warning_window.show()
        
        self.warning_timer.setInterval(warning_secs * 1000)
        self.warning_timer.start()
        
    def start_break(self):
        """开始休息"""
        self.warning_timer.stop()
        if self.warning_window:
            self.warning_window.close()
            
        break_mins = self.config.get("screensaver.break_duration")
        self.screen_saver = ScreenSaver()
        self.screen_saver.show()
        
        self.break_timer.setInterval(break_mins * 60 * 1000)
        self.break_timer.start()
        self.break_started.emit()
        
    def finish_break(self):
        """结束休息"""
        self.break_timer.stop()
        if self.screen_saver:
            self.screen_saver.close()
            
        self.work_timer.start()
        self.break_finished.emit() 