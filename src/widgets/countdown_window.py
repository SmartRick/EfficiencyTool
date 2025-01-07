from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from utils.config import Config

class CountdownWindow(QWidget):
    """透明倒计时窗口"""
    def __init__(self, total_minutes, parent=None):
        super().__init__(parent)
        self.total_seconds = total_minutes * 60
        self.current_seconds = self.total_seconds
        
        # 设置窗口标志
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |  # 不在任务栏显示
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)  # 显示时不激活窗口
        
        self.config = Config()
        
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 从配置中获取样式
        font_family = self.config.get('countdown.font_family', 'SF Pro Display')
        font_size = self.config.get('countdown.font_size', 48)
        color = self.config.get('countdown.color', 'rgba(0, 122, 255, 0.8)')
        opacity = self.config.get('countdown.opacity', 0.8)
        
        # 创建时间标签
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont(font_family, font_size, QFont.Bold))
        self.time_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background: transparent;
            }}
        """)
        
        layout.addWidget(self.time_label)
        
        # 设置窗口大小和位置
        self.resize(200, 120)
        self.move_to_corner()
        
        self.update_time_display()
        
        # 设置窗口透明度
        self.setWindowOpacity(opacity)
    
    def setup_timer(self):
        """设置定时器"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # 每秒更新一次
    
    def update_countdown(self):
        """更新倒计时"""
        self.current_seconds -= 1
        if self.current_seconds <= 0:
            self.timer.stop()
            self.close()
        self.update_time_display()
    
    def update_time_display(self):
        """更新显示的时间"""
        minutes = self.current_seconds // 60
        seconds = self.current_seconds % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def move_to_corner(self):
        """移动到屏幕右上角"""
        screen = self.screen()
        screen_geometry = screen.geometry()
        
        # 计算位置（右上角，留出一定边距）
        x = screen_geometry.width() - self.width() - 40
        y = 40
        
        self.move(x, y)
    
    def closeEvent(self, event):
        """窗口关闭时停止计时器"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept() 