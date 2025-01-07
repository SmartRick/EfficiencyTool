from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer

class WarningWindow(QWidget):
    """休息提醒窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置窗口标志
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |  # 不在任务栏显示
            Qt.SubWindow  # 子窗口模式
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # 初始化UI
        self.init_ui()
        
        # 设置定时器
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        self.label = QLabel(f"将在 {self.countdown} 秒后开始休息...")
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        
        layout.addWidget(self.label)
        
        # 设置窗口位置
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() - 250,
            screen.height() - 100,
            200,
            50
        )
        
    def update_countdown(self):
        """更新倒计时"""
        self.countdown -= 1
        self.label.setText(f"将在 {self.countdown} 秒后开始休息...")
        
        if self.countdown <= 0:
            self.timer.stop()
            self.close() 