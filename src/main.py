import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QMediaPlayer
from window import MainWindow
import os
import qtawesome as qta

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.logger = logging.getLogger('Application')
        
        # 初始化多媒体系统
        try:
            # 创建一个临时的 QMediaPlayer 来初始化多媒体系统
            self._player = QMediaPlayer()
            self.logger.info('Multimedia system initialized')
        except Exception as e:
            self.logger.error(f'Failed to initialize multimedia system: {e}')
        
        # 设置应用程序属性
        self.setQuitOnLastWindowClosed(False)
        
        # 创建主窗口
        self.window = MainWindow()
        self.window.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint
        )
        
        self.window.show()
        self.logger.info('Application started')

if __name__ == '__main__':
    app = Application(sys.argv)
    sys.exit(app.exec())