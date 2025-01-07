from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QEvent, QTimer
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtGui import (
    QPixmap, QColor, QKeySequence, QShortcut, 
    QGuiApplication, QImage
)
from utils.config import Config
import os

# 尝试导入视频组件
try:
    from PySide6.QtMultimediaWidgets import QVideoWidget
    VIDEO_SUPPORT = True
except ImportError:
    VIDEO_SUPPORT = False

class ScreenSaver(QWidget):
    """全屏屏保窗口"""
    closed = Signal()  # 添加关闭信号
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.preview_mode = False
        
        # 读取是否允许关闭的配置
        self.allow_close = self.config.get('screensaver.allow_close', False)
        
        # 添加预览定时器
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)  # 设置为单次触发
        self.preview_timer.timeout.connect(self.close_preview)
        
        # 修改窗口标志，解决图层更新问题
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |  # 避免任务栏显示
            Qt.NoDropShadowWindowHint  # 添加此标志避免阴影问题
        )
        
        # 修改窗口属性
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_AlwaysStackOnTop)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)  # 确保窗口可以正常激活
        self.setAttribute(Qt.WA_NoSystemBackground, False)  # 允许系统背景
        
        # 创建遮罩层
        self.mask_widget = QWidget(self)
        self.mask_widget.setStyleSheet("background-color: transparent;")
        self.mask_widget.setMouseTracking(True)
        self.mask_widget.installEventFilter(self)
        
        # 设置焦点检查定时器
        self.focus_check_timer = QTimer(self)
        self.focus_check_timer.timeout.connect(self._check_focus)
        self.focus_check_timer.start(500)  # 降低检查频率
        
        self.init_ui()
        self.setup_hotkey()
        
        self.can_close = False
        self.video_playing = False
        
    def ensure_top_window(self):
        """优化确保窗口保持在最前的逻辑"""
        if not self.preview_mode and not self.isActiveWindow():
            self.raise_()
            self.activateWindow()
            self._force_focus()
            
            # 只在真正需要时处理多屏幕
            current_screen = self.screen()
            for screen in QGuiApplication.screens():
                if screen != current_screen:
                    self.windowHandle().setScreen(screen)
                    self.showFullScreen()
    
    def _check_focus(self):
        """持续检查并维持焦点"""
        if not self.preview_mode and not self.hasFocus():
            self._force_focus()
    
    def eventFilter(self, obj, event):
        if not self.preview_mode:
            event_type = event.type()
            
            # 批量处理鼠标和焦点事件
            if event_type in (
                QEvent.MouseButtonPress, 
                QEvent.MouseButtonRelease,
                QEvent.MouseMove,
                QEvent.MouseButtonDblClick,
                QEvent.WindowDeactivate,
                QEvent.FocusOut
            ):
                event.accept()
                QTimer.singleShot(100, self._force_focus)
                return True
        
        return super().eventFilter(obj, event)
    
    def showEvent(self, event):
        """优化窗口显示逻辑"""
        super().showEvent(event)
        
        # 如果是预览模式，启动预览定时器
        if self.preview_mode:
            preview_duration = self.config.get('screensaver.preview_duration', 5000)  # 默认5秒
            self.preview_timer.start(preview_duration)
        
        # 确保在显示前设置正确的几何形状
        screen = self.screen()
        if screen:
            self.setGeometry(screen.geometry())
        
        # 设置遮罩层
        self.mask_widget.setGeometry(self.rect())
        self.mask_widget.raise_()
        self.mask_widget.show()
        
        # 使用延迟显示全屏
        QTimer.singleShot(50, self._show_fullscreen)
        
        # 设置焦点
        self.setFocus(Qt.ActiveWindowFocusReason)
        self.mask_widget.setFocus(Qt.ActiveWindowFocusReason)
    
    def _show_fullscreen(self):
        """延迟显示全屏"""
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        
        if self.windowHandle():
            self.windowHandle().requestActivate()
        
        # 强制重绘
        self.repaint()
    
    def _force_focus(self):
        """简化焦点设置"""
        if not self.preview_mode:
            self.raise_()
            self.activateWindow()
            self.setFocus()
            
            if self.windowHandle():
                self.windowHandle().requestActivate()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 获取媒体配置
        media_type = self.config.get('screensaver.media_type', 'image')
        media_path = self.config.get('screensaver.media_path', 'assets/default_wallpaper.jpg')
        
        if VIDEO_SUPPORT and media_type == 'video' and os.path.exists(media_path):
            self.setup_video(media_path)
        else:
            self.setup_image(media_path)
    
    def setup_video(self, media_path):
        """优化视频播放设置"""
        try:
            self.player = QMediaPlayer()
            self.video_widget = QVideoWidget()  # 先创建 video_widget
            
            # 设置视频窗口属性
            self.video_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.video_widget.setAspectRatioMode(Qt.KeepAspectRatio)
            
            # 设置优先使用软解码
            self.player.setVideoOutput(self.video_widget)
            
            # 设置低延迟模式
            if hasattr(self.player, 'setLowLatency'):
                self.player.setLowLatency(True)
            
            # 设置缓冲模式
            if hasattr(self.player, 'setBufferSize'):
                self.player.setBufferSize(4096)
            
            self.player.setSource(media_path)
            self.player.setLoops(QMediaPlayer.Infinite)  # 添加循环播放设置
            
            # 添加错误处理
            self.player.errorOccurred.connect(self._handle_video_error)
            
            self.layout().addWidget(self.video_widget)
            
            # 连接状态变化信号
            self.player.playbackStateChanged.connect(self._on_playback_state_changed)
            
            # 延迟播放以确保窗口准备就绪
            video_delay = self.config.get('screensaver.video_start_delay', 100)
            QTimer.singleShot(video_delay, self.player.play)
            self.video_playing = True
        except Exception as e:
            print(f"视频播放初始化失败: {e}")
            # 如果视频播放失败，回退到图片模式
            self.setup_image(self.config.get('screensaver.media.path', 'assets/default_wallpaper.jpg'))
    
    def _on_playback_state_changed(self, state):
        """处理视频播放状态变化"""
        if state == QMediaPlayer.StoppedState and self.video_playing:
            self.player.play()
    
    def setup_image(self, media_path):
        """优化图片加载和显示"""
        label = QLabel(self)
        label.setAlignment(Qt.AlignCenter)
        
        if os.path.exists(media_path):
            # 使用 QImage 加载和缩放
            image = QImage(media_path)
            screen_size = self.screen().size()
            
            # 预缩放大图片
            if image.width() > screen_size.width() * 2 or image.height() > screen_size.height() * 2:
                image = image.scaled(
                    screen_size.width() * 2,
                    screen_size.height() * 2,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            
            # 最终缩放
            scaled_image = image.scaled(
                screen_size,
                Qt.KeepAspectRatio,
                Qt.FastTransformation
            )
            
            label.setPixmap(QPixmap.fromImage(scaled_image))
        else:
            # 默认黑色背景
            pixmap = QPixmap(100, 100)
            pixmap.fill(QColor("#000000"))
            label.setPixmap(pixmap)
        
        self.layout().addWidget(label)
    
    def setup_hotkey(self):
        """设置快捷键"""
        hotkey = self.config.get('screensaver.hotkey', 'Ctrl+0')
        self.shortcut = QShortcut(QKeySequence(hotkey), self)
        self.shortcut.activated.connect(self.close_screensaver)
    
    def close_screensaver(self):
        """通过快捷键关闭"""
        # 检查是否允许关闭
        if not self.allow_close and not self.preview_mode:
            return  # 如果不允许关闭且不是预览模式,直接返回
        
        self.closing_by_hotkey = True
        self.can_close = True
        self.close()
    
    def closeEvent(self, event):
        """重写关闭事件"""
        if hasattr(self, 'focus_check_timer'):
            self.focus_check_timer.stop()
            
        # 停止视频播放
        if hasattr(self, 'player'):
            self.video_playing = False
            self.player.stop()
            
        # 检查是否允许关闭
        if self.preview_mode or (self.allow_close and hasattr(self, 'closing_by_hotkey') and self.closing_by_hotkey):
            if hasattr(self, 'keep_top_timer'):
                self.keep_top_timer.stop()
            event.accept()
            self.closed.emit()
        else:
            event.ignore()
            
        # 停止预览定时器
        if hasattr(self, 'preview_timer'):
            self.preview_timer.stop()
            
        super().closeEvent(event)
    
    def keyPressEvent(self, event):
        """处理按键事件"""
        if self.preview_mode:
            # 在预览模式下，按任意键都会关闭窗口
            self.can_close = True
            self.close()
        else:
            super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        """窗口大小改变时调整遮罩层大小"""
        super().resizeEvent(event)
        if hasattr(self, 'mask_widget'):
            self.mask_widget.setGeometry(self.rect())
            self.mask_widget.raise_()
    
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if not self.preview_mode:
            event.accept()
            self.mask_widget.raise_()
            self._force_focus()
        
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if not self.preview_mode:
            event.accept()
            self.mask_widget.raise_()
            self._force_focus()
        
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if not self.preview_mode:
            event.accept()
            self.mask_widget.raise_()
            self._force_focus()
        
    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件"""
        if not self.preview_mode:
            event.accept()
            self.mask_widget.raise_()
            self._force_focus() 
    
    def _handle_video_error(self, error, error_string):
        """处理视频播放错误"""
        print(f"视频播放错误: {error_string}")
        if self.video_playing:
            self.video_playing = False
            # 出错时回退到图片模式
            self.setup_image(self.config.get('screensaver.media.path', 'assets/default_wallpaper.jpg')) 
    
    def close_preview(self):
        """关闭预览"""
        if self.preview_mode:
            self.can_close = True
            self.close() 