from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpacerItem, QSizePolicy,
    QGraphicsDropShadowEffect, QGroupBox, QRadioButton,
    QFileDialog, QInputDialog, QGraphicsOpacityEffect,
    QSystemTrayIcon, QMenu, QApplication
)
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QSize, QTimer, QEvent
from PySide6.QtGui import QFont, QMouseEvent, QColor, QPixmap, QPainter, QBrush
import qtawesome as qta
from screensaver.manager import ScreenSaverManager
from utils.style import StyleManager
from utils.config import Config
import os
from PySide6.QtCore import Signal
from widgets.countdown_window import CountdownWindow
from widgets.sidebar import Sidebar
from widgets.page_container import PageContainer
from widgets.control_panel import ControlPanel

class CustomButton(QPushButton):
    """macOS 风格按钮"""
    def __init__(self, text, parent=None, primary=True, **kwargs):
        super().__init__(text, parent)
        self.style_manager = StyleManager()
        
        # 设置大小
        width = kwargs.get('width', 200)
        height = kwargs.get('height', 36)
        self.setFixedSize(width, height)
        
        # 设置图标
        icon_name = kwargs.get('icon', '')
        if icon_name:
            icon_color = kwargs.get('icon_color', 'white' if primary else '#666666')
            icon_size = kwargs.get('icon_size', 16)
            self.setIcon(qta.icon(icon_name, color=icon_color))
            self.setIconSize(QSize(icon_size, icon_size))
        
        # 设置样式
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: #007AFF;
                    border: none;
                    border-radius: 6px;
                    color: white;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: #0062CC;
                }
                QPushButton:pressed {
                    background: #005AB5;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: #F5F5F7;
                    border: 1px solid #E5E5E5;
                    border-radius: 6px;
                    color: #333333;
                    font-size: 13px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background: #EAEAEB;
                }
                QPushButton:pressed {
                    background: #DCDCDC;
                }
            """)

class MacButton(QPushButton):
    """macOS 风格窗口控制按钮"""
    def __init__(self, button_type, parent=None):
        super().__init__(parent)
        self.button_type = button_type
        self.setFixedSize(12, 12)
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 6px;
            }
        """)
        
        # 设置默认颜色
        self.colors = {
            'close': {'default': '#FF5F57', 'hover': '#FF4A4A'},
            'minimize': {'default': '#FEBC2E', 'hover': '#FEB321'},
            'maximize': {'default': '#28C840', 'hover': '#24B539'}
        }
        
        self.is_hovered = False
        
    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        
    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        
    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QBrush
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取当前颜色
        color_state = 'hover' if self.is_hovered else 'default'
        color = self.colors[self.button_type][color_state]
        
        # 绘制按钮
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 12, 12)

class TitleBar(QWidget):
    """自定义标题栏"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.style_manager = StyleManager()
        self.parent = parent
        self.setObjectName("titleBar")
        
        # 设置固定高度
        height = self.style_manager.config.get('title_bar.height', 38)
        self.setFixedHeight(height)
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        # macOS 风格控制按钮
        btn_close = MacButton('close', self)
        btn_min = MacButton('minimize', self)
        btn_max = MacButton('maximize', self)
        
        btn_close.clicked.connect(self.parent.quit_application)
        btn_min.clicked.connect(self.minimize_to_tray)
        
        # 按钮容器
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        buttons_layout.addWidget(btn_close)
        buttons_layout.addWidget(btn_min)
        buttons_layout.addWidget(btn_max)
        
        # 标题
        title = QLabel("休息提醒")
        title.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 13px;
                font-weight: 500;
            }
        """)
        
        # 添加设置按钮
        settings_button = QPushButton(self)
        settings_button.setIcon(qta.icon('fa5s.cog', color='#666666'))
        settings_button.setFixedSize(32, 32)
        settings_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                padding: 6px;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.05);
                border-radius: 4px;
            }
        """)
        settings_button.clicked.connect(self.parent.show_settings)
        
        layout.addLayout(buttons_layout)
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addStretch(1)
        layout.addWidget(settings_button)  # 添加设置按钮到布局
        
    def minimize_to_tray(self):
        """最小化到托盘"""
        self.parent.hide()
        self.parent.tray_icon.showMessage(
            "休息提醒",
            "应用程序已最小化到系统托盘",
            QSystemTrayIcon.Information,
            2000
        )
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.drag_position = event.globalPos() - self.parent.pos()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.parent.move(event.globalPos() - self.parent.drag_position)
            event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.style_manager = StyleManager()
        
        # 设置窗口尺寸范围
        self.setMinimumSize(700, 600)
        self.setMaximumSize(1000, 900)
        
        # 修改窗口标志 - 添加 Qt.Tool 使窗口不在任务栏显示
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowMaximizeButtonHint |
            Qt.Tool
        )
        
        # 设置透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 初始化UI
        self.init_ui()
        self.setSizeGripEnabled(True)
        self.center_window()
        
        # 添加关闭标志
        self.can_close = True
        
        self.show_animation = QPropertyAnimation(self, b"windowOpacity")
        self.show_animation.setDuration(200)
        self.show_animation.setStartValue(0)
        self.show_animation.setEndValue(1)
        self.show_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 添加系统托盘相关属性
        self.tray_icon = None
        self.tray_menu = None
        self.init_tray()
        
        # 设置窗口接收键盘焦点
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAttribute(Qt.WA_KeyboardFocusChange)
        
        self.is_preview_mode = False  # 添加预览模式标志
        
        # 添加全屏标志
        self.is_fullscreen_mode = False
        
    def init_ui(self):
        # 创建主容器
        self.container = QWidget()
        self.setCentralWidget(self.container)
        
        # 创建内容窗口.
        self.window_content = QWidget(self.container)
        self.window_content.setObjectName("windowContent")
        
        # 设置布局
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.addWidget(self.window_content)
        
        # 内容布局
        layout = QVBoxLayout(self.window_content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 添加标题栏
        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)
        
        # 创建主内容区域
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 添加侧边栏
        self.sidebar = Sidebar()
        self.sidebar.pageChanged.connect(self.on_page_changed)
        content_layout.addWidget(self.sidebar)
        
        # 添加页面容器
        self.page_container = PageContainer()
        content_layout.addWidget(self.page_container)
        
        layout.addWidget(content)
        
        # 应用样式
        self.setStyleSheet(self.style_manager.get_style('main_window'))
        
        # 添加阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow_config = self.style_manager.get_global_config('shadow', {})
        shadow.setBlurRadius(shadow_config.get('blur_radius', 20))
        shadow.setColor(QColor(shadow_config.get('color', 'rgba(0, 0, 0, 0.1)')))
        offset = shadow_config.get('offset', [0, 4])
        shadow.setOffset(offset[0], offset[1])
        self.window_content.setGraphicsEffect(shadow)
        
        # 添加系统托盘相关属性
        self.tray_icon = None
        self.tray_menu = None
        self.init_tray()
        
    def init_tray(self):
        """初始化系统托盘"""
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        icon = qta.icon('fa5s.clock', color='#333333')
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip('休息提醒')
        
        # 创建托盘菜单
        self.tray_menu = QMenu()
        show_action = self.tray_menu.addAction("显示")
        show_action.triggered.connect(self.show_from_tray)
        
        settings_action = self.tray_menu.addAction("设置")
        settings_action.triggered.connect(self.show_settings)
        
        self.tray_menu.addSeparator()
        
        quit_action = self.tray_menu.addAction("退出")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # 连接托盘图标的点击事件
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        
    def show_from_tray(self):
        """从托盘显示窗口"""
        self.show()
        self.activateWindow()
        
    def quit_application(self):
        """退出应用程序"""
        self.can_close = True
        self.close()
        QApplication.quit()
        
    def on_tray_icon_activated(self, reason):
        """处理托盘图标的激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_from_tray()
        
    def showEvent(self, event):
        super().showEvent(event)
        # self.show_animation.start()  # 注释掉动画启动
        
    def center_window(self):
        screen = self.screen()
        center_point = screen.geometry().center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        
    def on_break_started(self):
        """休息开始"""
        self.hide()  # 隐藏主窗口
        
    def on_break_finished(self):
        """休息结束"""
        self.show()  # 显示主窗口 
        
    def show_settings(self):
        """显示设置窗口"""
        from widgets.settings_window import SettingsWindow
        settings = SettingsWindow(self)
        settings.show()
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        if self.can_close:
            event.accept()
        else:
            event.ignore()
            self.hide()  # 隐藏窗口而不是关闭
    
    def on_page_changed(self, page_id):
        """处理页面切换"""
        page_index = {
            'break': 0,
            'todo': 1,
            'notes': 2,
            'settings': 3
        }.get(page_id, 0)
        
        self.page_container.setCurrentIndex(page_index)
    
    def setSizeGripEnabled(self, enabled):
        """启用大小调整"""
        if enabled:
            self.setMouseTracking(True)
            self.centralWidget().setMouseTracking(True)
        else:
            self.setMouseTracking(False)
            self.centralWidget().setMouseTracking(False)
    
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if self.is_fullscreen_mode:
            event.accept()  # 在全屏模式下吞掉所有鼠标事件
        else:
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if self.is_fullscreen_mode:
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if self.is_fullscreen_mode:
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件"""
        if self.is_fullscreen_mode:
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)
    
    def is_resize_area(self, pos):
        """判断是否在调整区域"""
        margin = 5
        # 获取窗口内容的几何信息
        content_rect = self.window_content.geometry()
        
        # 检查是否在边框区域
        return (
            pos.x() <= content_rect.left() + margin or 
            pos.x() >= content_rect.right() - margin or
            pos.y() <= content_rect.top() + margin or
            pos.y() >= content_rect.bottom() - margin
        )
    
    def get_resize_mode(self, pos):
        """获取调整模式"""
        margin = 5
        content_rect = self.window_content.geometry()
        
        # 返回调整方向
        if pos.x() <= content_rect.left() + margin:
            return 'left'
        elif pos.x() >= content_rect.right() - margin:
            return 'right'
        elif pos.y() <= content_rect.top() + margin:
            return 'top'
        else:
            return 'bottom'
    
    def get_resize_cursor(self, pos):
        """获取调整光标"""
        if not self.is_resize_area(pos):
            return Qt.ArrowCursor
            
        mode = self.get_resize_mode(pos)
        if mode in ['left', 'right']:
            return Qt.SizeHorCursor
        else:
            return Qt.SizeVerCursor
    
    def do_resize(self, global_pos):
        """执行大小调整"""
        if not hasattr(self, 'resize_mode'):
            return
            
        rect = self.geometry()
        delta = global_pos - rect.topLeft()
        
        if self.resize_mode == 'right':
            width = max(self.minimumWidth(), delta.x())
            self.resize(width, rect.height())
        elif self.resize_mode == 'bottom':
            height = max(self.minimumHeight(), delta.y())
            self.resize(rect.width(), height)
        elif self.resize_mode == 'left':
            width = max(self.minimumWidth(), rect.right() - global_pos.x())
            self.resize(width, rect.height())
            self.move(global_pos.x(), rect.y())
        elif self.resize_mode == 'top':
            height = max(self.minimumHeight(), rect.bottom() - global_pos.y())
            self.resize(rect.width(), height)
            self.move(rect.x(), global_pos.y())
    
    def leaveEvent(self, event):
        """处理鼠标离开窗口事件"""
        if not hasattr(self, 'resize_mode'):  # 如果不在调整大小状态
            self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)
    
    def changeEvent(self, event):
        """处理窗口状态改变事件"""
        if event.type() == QEvent.Type.WindowStateChange:
            if self.windowState() & Qt.WindowState.Minimized:
                event.accept()
                self.hide()  # 最小化时隐藏窗口
                # 可选：显示托盘通知
                self.tray_icon.showMessage(
                    "休息提醒",
                    "应用程序已最小化到系统托盘",
                    QSystemTrayIcon.Information,
                    2000
                )

    def keyPressEvent(self, event):
        """处理按键事件"""
        if self.is_preview_mode:  # 简化判断条件
            print("Key pressed in preview mode")  # 添加调试输出
            self.set_fullscreen_mode(False)
            self.hide()
            self.is_preview_mode = False
            event.accept()
        else:
            super().keyPressEvent(event)

    def show_preview(self):
        """显示预览模式"""
        try:
            self.is_preview_mode = True
            self.set_fullscreen_mode(True)
            self.setFocus()
            
            # 强制重绘
            self.repaint()
            
        except Exception as e:
            print(f"预览模式显示失败: {e}")
            # 恢复正常模式
            self.is_preview_mode = False
            self.set_fullscreen_mode(False)
    
    def set_fullscreen_mode(self, enabled=True):
        """设置全屏模式"""
        self.is_fullscreen_mode = enabled
        if enabled:
            # 设置全屏且阻止其他窗口交互的标志
            self.setWindowFlags(
                Qt.Window |
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint |  # 保持在最顶层
                Qt.X11BypassWindowManagerHint |  # X11系统绕过窗口管理器
                Qt.WindowDoesNotAcceptFocus |  # 不接受焦点，阻止输入法
                Qt.BypassWindowManagerHint  # 添加这个标志以更好地控制窗口行为
            )
            # 设置窗口属性
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setAttribute(Qt.WA_NoSystemBackground)
            self.setAttribute(Qt.WA_AlwaysStackOnTop)  # 始终保持在顶部
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)  # 确保捕获鼠标事件
            
            # 获取屏幕大小并全屏显示
            screen = self.screen()
            self.setGeometry(screen.geometry())
            self.showFullScreen()
        else:
            # 恢复普通窗口标志
            self.setWindowFlags(
                Qt.Window |
                Qt.FramelessWindowHint |
                Qt.WindowMaximizeButtonHint |
                Qt.Tool
            )
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.showNormal()
            
        # 确保窗口可见性
        self.show()
        self.raise_()
        self.activateWindow()

class TimeSpinBox(QWidget):
    """时间调节控件"""
    valueChanged = Signal(int)  # 添加信号
    
    def __init__(self, value, min_value=1, max_value=120, parent=None):
        super().__init__(parent)
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 减少按钮
        self.decrease_btn = QPushButton(self)
        self.decrease_btn.setIcon(qta.icon('fa5s.minus', color='#666666'))
        self.decrease_btn.setFixedSize(24, 24)
        self.decrease_btn.clicked.connect(self.decrease)
        
        # 数值显示
        self.value_label = QLabel(str(self.value))
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setFixedWidth(32)
        
        # 增加按钮
        self.increase_btn = QPushButton(self)
        self.increase_btn.setIcon(qta.icon('fa5s.plus', color='#666666'))
        self.increase_btn.setFixedSize(24, 24)
        self.increase_btn.clicked.connect(self.increase)
        
        # 分钟标签
        self.unit_label = QLabel("分钟")
        self.unit_label.setStyleSheet("color: #666666;")
        
        # 设置样式
        style = """
            QPushButton {
                background: #F5F5F7;
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background: #EAEAEB;
            }
            QPushButton:pressed {
                background: #DCDCDC;
            }
            QLabel {
                font-size: 13px;
                color: #333333;
            }
        """
        self.setStyleSheet(style)
        
        # 添加到布局
        layout.addWidget(self.decrease_btn)
        layout.addWidget(self.value_label)
        layout.addWidget(self.increase_btn)
        layout.addWidget(self.unit_label)
        layout.addStretch()
    
    def decrease(self):
        if self.value > self.min_value:
            self.value -= 1
            self.value_label.setText(str(self.value))
            self.valueChanged.emit(self.value)
    
    def increase(self):
        if self.value < self.max_value:
            self.value += 1
            self.value_label.setText(str(self.value))
            self.valueChanged.emit(self.value)
    
    def get_value(self):
        return self.value 

class MediaDropArea(QWidget):
    """媒体文件拖放区域"""
    mediaDropped = Signal(str)  # 文件拖放信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.control_panel = self.get_control_panel()  # 获取 ControlPanel 实例
        self.init_ui()
    
    def get_control_panel(self):
        """获取 ControlPanel 实例"""
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, ControlPanel):
                return parent
            parent = parent.parent()
        return None
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 创建预览区域
        self.preview = QLabel()
        self.preview.setFixedSize(200, 120)
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet("""
            QLabel {
                background: #F5F5F7;
                border: 2px dashed #E5E5E5;
                border-radius: 6px;
            }
        """)
        
        # 提示文本
        self.hint_label = QLabel("拖放文件到此处或点击选择")
        self.hint_label.setStyleSheet("""
            color: #666666;
            font-size: 13px;
        """)
        self.hint_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.preview, alignment=Qt.AlignCenter)
        layout.addWidget(self.hint_label, alignment=Qt.AlignCenter)
    
    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls() and len(mime_data.urls()) == 1:
            file_path = mime_data.urls()[0].toLocalFile()
            if self.is_valid_file(file_path):
                event.acceptProposedAction()
                self.preview.setStyleSheet("""
                    QLabel {
                        background: #F5F5F7;
                        border: 2px dashed #007AFF;
                        border-radius: 6px;
                    }
                """)
    
    def dragLeaveEvent(self, event):
        self.preview.setStyleSheet("""
            QLabel {
                background: #F5F5F7;
                border: 2px dashed #E5E5E5;
                border-radius: 6px;
            }
        """)
    
    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.update_preview(file_path)
        self.mediaDropped.emit(file_path)
        self.preview.setStyleSheet("""
            QLabel {
                background: #F5F5F7;
                border: 2px dashed #E5E5E5;
                border-radius: 6px;
            }
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.control_panel.choose_file()  # 使用 control_panel 替代 parent()
    
    def is_valid_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if self.control_panel.image_radio.isChecked():  # 使用 control_panel 替代 parent()
            return ext in ['.jpg', '.jpeg', '.png', '.bmp']
        else:
            return ext in ['.mp4', '.avi', '.mkv']
    
    def update_preview(self, file_path):
        if os.path.exists(file_path):
            if self.control_panel.image_radio.isChecked():
                pixmap = QPixmap(file_path)
                scaled_pixmap = pixmap.scaled(
                    self.preview.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview.setPixmap(scaled_pixmap)
            else:
                # 显示视频缩略图或图标
                self.preview.setPixmap(qta.icon('fa5s.film', color='#666666').pixmap(48, 48)) 