from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSpacerItem, QSizePolicy, QGroupBox,
    QRadioButton, QFileDialog, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer, QMimeData, QUrl, QSize
from PySide6.QtGui import (
    QDragEnterEvent, QDropEvent, QPixmap, 
    QPainter, QColor, QImage
)
from PySide6.QtMultimedia import QMediaPlayer, QMediaMetaData
from PySide6.QtMultimediaWidgets import QVideoWidget
import qtawesome as qta
from utils.config import Config
from utils.style import StyleManager
from widgets.countdown_window import CountdownWindow
from screensaver.screen_saver import ScreenSaver
from widgets.time_spinbox import TimeSpinBox
import os
import cv2
import numpy as np

class MediaDropArea(QWidget):
    """媒体文件拖放区域"""
    def __init__(self, control_panel, parent=None):
        super().__init__(parent)
        self.control_panel = control_panel
        self.setAcceptDrops(True)
        
        # 设置固定高度范围
        self.setMinimumHeight(160)
        self.setMaximumHeight(200)
        self.setCursor(Qt.PointingHandCursor)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建预览容器
        self.preview_container = QWidget()
        self.preview_container.setObjectName("previewContainer")
        preview_layout = QVBoxLayout(self.preview_container)
        preview_layout.setAlignment(Qt.AlignCenter)
        
        # 创建预览标签
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.preview_label)
        
        # 创建操作按钮容器
        self.action_container = QWidget()
        self.action_container.setObjectName("actionContainer")
        action_layout = QVBoxLayout(self.action_container)
        action_layout.setAlignment(Qt.AlignCenter)
        
        # 创建提示图标
        hint_icon = QLabel()
        hint_icon.setPixmap(qta.icon('fa5s.cloud-upload-alt', color='#666666').pixmap(48, 48))
        hint_icon.setAlignment(Qt.AlignCenter)
        
        # 创建提示文本
        hint_text = QLabel("拖放文件到此处\n或")
        hint_text.setAlignment(Qt.AlignCenter)
        hint_text.setStyleSheet("color: #666666;")
        
        # 创建选择按钮
        self.choose_btn = QPushButton("选择文件")
        self.choose_btn.setFixedWidth(120)
        self.choose_btn.setStyleSheet("""
            QPushButton {
                background: #F5F5F7;
                border: 1px solid #E5E5E5;
                border-radius: 6px;
                color: #333333;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #EAEAEB;
                border-color: #007AFF;
            }
        """)
        
        action_layout.addWidget(hint_icon)
        action_layout.addWidget(hint_text)
        action_layout.addWidget(self.choose_btn)
        
        # 添加到主布局
        layout.addWidget(self.preview_container)
        layout.addWidget(self.action_container)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QWidget#previewContainer {
                background: #F5F5F7;
                border: 2px dashed #E5E5E5;
                border-radius: 8px;
            }
            QWidget#previewContainer:hover {
                border-color: #007AFF;
                background: #F0F9FF;
            }
            QLabel {
                font-size: 13px;
            }
        """)
        
        # 默认隐藏预览容器
        self.preview_container.hide()
        
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            # 点击整个区域都可以选择文件
            self.choose_btn.click()
    
    def update_preview(self, pixmap=None):
        """更新预览"""
        if pixmap:
            # 显示预览图
            scaled_pixmap = pixmap.scaled(
                self.width() - 40,  # 留出边距
                self.height() - 40,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
            self.preview_container.show()
            self.action_container.hide()
            
            # 添加更换文件的提示
            self.setToolTip("点击更换文件")
        else:
            # 显示拖放提示
            self.preview_container.hide()
            self.action_container.show()
            self.setToolTip("")  # 清除提示
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QWidget#previewContainer {
                    background: #F0F9FF;
                    border: 2px dashed #007AFF;
                    border-radius: 8px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        """处理拖离事件"""
        self.setStyleSheet("""
            QWidget#previewContainer {
                background: #F5F5F7;
                border: 2px dashed #E5E5E5;
                border-radius: 8px;
            }
            QWidget#previewContainer:hover {
                border-color: #007AFF;
                background: #F0F9FF;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        """处理放下事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.control_panel.handle_dropped_file(file_path)
        self.dragLeaveEvent(None)

class ControlPanel(QWidget):
    """控制面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.style_manager = StyleManager()
        
        # 获取配置的时间
        self.work_time = self.config.get('screensaver.work_duration', 25)
        self.break_time = self.config.get('screensaver.break_duration', 5)
        
        self.init_ui()
        
        # 初始化完成后更新预览
        QTimer.singleShot(100, self.update_preview)  # 使用延时确保组件已完全初始化
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 设置 QScrollArea 使内容可滚动
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        
        # 时间设置组
        time_group = QGroupBox("时间设置")
        time_layout = QVBoxLayout(time_group)
        
        # 工作时间
        work_time_layout = QHBoxLayout()
        work_time_label = QLabel("工作时间")
        work_time_label.setStyleSheet("color: #666666;")
        
        self.work_time_spin = TimeSpinBox(self.work_time)
        self.work_time_spin.valueChanged.connect(self.on_work_time_changed)
        
        work_time_layout.addWidget(work_time_label)
        work_time_layout.addWidget(self.work_time_spin)
        
        # 休息时间
        break_time_layout = QHBoxLayout()
        break_time_label = QLabel("休息时间")
        break_time_label.setStyleSheet("color: #666666;")
        
        self.break_time_spin = TimeSpinBox(self.break_time)
        self.break_time_spin.valueChanged.connect(self.on_break_time_changed)
        
        break_time_layout.addWidget(break_time_label)
        break_time_layout.addWidget(self.break_time_spin)
        
        time_layout.addLayout(work_time_layout)
        time_layout.addLayout(break_time_layout)
        
        # 屏保设置组
        screensaver_group = QGroupBox("屏保设置")
        screensaver_layout = QVBoxLayout(screensaver_group)
        screensaver_layout.setSpacing(16)  # 增加间距
        
        # 媒体类型选择
        media_type_layout = QHBoxLayout()
        self.image_radio = QRadioButton("图片")
        self.video_radio = QRadioButton("视频")
        
        current_type = self.config.get('screensaver.media_type', 'image')
        if current_type == 'video':
            self.video_radio.setChecked(True)
        else:
            self.image_radio.setChecked(True)
        
        self.image_radio.toggled.connect(self.on_media_type_changed)
        self.video_radio.toggled.connect(self.on_media_type_changed)
        
        media_type_layout.addWidget(self.image_radio)
        media_type_layout.addWidget(self.video_radio)
        media_type_layout.addStretch()
        
        # 媒体文件选择区域
        self.drop_area = MediaDropArea(self)
        self.drop_area.choose_btn.clicked.connect(self.choose_media_file)
        
        # 预览按钮
        preview_button = QPushButton("预览效果")
        preview_button.clicked.connect(self.preview_screensaver)
        preview_button.setStyleSheet("""
            QPushButton {
                background: #F5F5F7;
                border: 1px solid #E5E5E5;
                border-radius: 6px;
                color: #333333;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: #EAEAEB;
                border-color: #007AFF;
            }
        """)
        
        # 添加到屏保布局
        screensaver_layout.addLayout(media_type_layout)
        screensaver_layout.addWidget(self.drop_area)
        screensaver_layout.addWidget(preview_button)
        
        # 开始按钮
        self.start_button = QPushButton("开始专注", self)
        self.start_button.setIcon(qta.icon('fa5s.play-circle', color='white'))
        self.start_button.clicked.connect(self.toggle_timer)
        self.start_button.setStyleSheet("""
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
        
        # 添加到主布局
        content_layout.addWidget(time_group)
        content_layout.addWidget(screensaver_group)
        content_layout.addStretch()
        content_layout.addWidget(self.start_button)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # 应用样式
        self.setStyleSheet(self.style_manager.get_style('control_panel'))
    
    def toggle_timer(self):
        """切换计时器状态"""
        if hasattr(self, 'work_timer') and self.work_timer.isActive():
            self.stop_timer()
        else:
            self.start_timer()
    
    def start_timer(self):
        """开始计时"""
        self.work_timer = QTimer(self)
        self.work_timer.timeout.connect(self.start_break)
        self.work_timer.start(self.work_time * 60 * 1000)  # 转换为毫秒
        
        # 创建并显示倒计时窗口
        self.countdown_window = CountdownWindow(self.work_time)
        self.countdown_window.show()
        
        self.start_button.setText("停止专注")
        self.start_button.setIcon(qta.icon('fa5s.stop-circle', color='white'))
    
    def stop_timer(self):
        """停止计时"""
        if hasattr(self, 'work_timer'):
            self.work_timer.stop()
        if hasattr(self, 'countdown_window'):
            self.countdown_window.close()
        self.start_button.setText("开始专注")
        self.start_button.setIcon(qta.icon('fa5s.play-circle', color='white'))
    
    def start_break(self):
        """开始休息"""
        # 停止工作计时器
        self.work_timer.stop()
        
        # 创建并显示屏保
        self.screen_saver = ScreenSaver()
        self.screen_saver.show()
        
        # 设置主窗口不可关闭
        self.window().can_close = False
        
        # 设置休息计时器
        self.break_timer = QTimer(self)
        self.break_timer.timeout.connect(self.end_break)
        self.break_timer.start(self.break_time * 60 * 1000)
        
        # 通知主窗口
        self.window().on_break_started()
    
    def end_break(self):
        """结束休息"""
        # 停止休息计时器
        self.break_timer.stop()
        
        # 关闭屏保
        if hasattr(self, 'screen_saver'):
            self.screen_saver.closing_by_hotkey = True
            self.screen_saver.close()
        
        # 重新开始工作计时器
        self.work_timer.start()
        
        # 恢复主窗口可关闭状态
        self.window().can_close = True
        
        # 通知主窗口
        self.window().on_break_finished()
    
    def on_work_time_changed(self, value):
        """工作时间改变"""
        self.work_time = value
        self.config.set('screensaver.work_duration', value)
    
    def on_break_time_changed(self, value):
        """休息时间改变"""
        self.break_time = value
        self.config.set('screensaver.break_duration', value)
    
    def on_media_type_changed(self, checked):
        """媒体类型改变时更新预览"""
        if checked:  # 只处理选中的事件
            media_type = 'video' if self.video_radio.isChecked() else 'image'
            self.config.set('screensaver.media_type', media_type)
            self.update_preview()  # 更新预览
    
    def preview_screensaver(self):
        """预览屏保"""
        # 如果有正在播放的视频，先停止
        if hasattr(self, 'media_player'):
            self.media_player.stop()
        
        self.preview_saver = ScreenSaver()
        self.preview_saver.preview_mode = True
        self.preview_saver.closed.connect(self.on_preview_closed)
        self.preview_saver.show()
        self.window().hide()
    
    def on_preview_closed(self):
        """预览结束"""
        self.window().show()
        if hasattr(self, 'preview_saver'):
            self.preview_saver.deleteLater()
            del self.preview_saver 
    
    def handle_dropped_file(self, file_path):
        """处理拖放的文件"""
        if self.check_file_type(file_path):
            self.config.set('screensaver.media_path', file_path)
            self.update_preview()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "文件类型错误",
                "请选择正确的文件类型：\n图片模式：jpg、jpeg、png、bmp\n视频模式：mp4、avi、mkv"
            )
    
    def update_preview(self):
        """更新预览"""
        media_path = self.config.get('screensaver.media_path', '')
        if not media_path or not os.path.exists(media_path):
            # 显示默认状态
            self.drop_area.update_preview(None)
            return
        
        if self.image_radio.isChecked():
            # 显示图片预览
            pixmap = QPixmap(media_path)
            self.drop_area.update_preview(pixmap)
        else:
            try:
                # 使用 OpenCV 获取视频第一帧作为缩略图
                cap = cv2.VideoCapture(media_path)
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    # 转换 BGR 到 RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    height, width, channel = frame.shape
                    
                    # 创建预览图
                    preview = QPixmap(self.drop_area.width() - 40, self.drop_area.height() - 40)
                    preview.fill(Qt.transparent)
                    
                    # 在预览图上绘制视频帧和文件信息
                    painter = QPainter(preview)
                    painter.setRenderHint(QPainter.Antialiasing)
                    
                    # 绘制背景
                    painter.setBrush(QColor('#F5F5F7'))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(0, 0, preview.width(), preview.height(), 8, 8)
                    
                    # 计算缩放后的视频帧大小
                    frame_height = preview.height() - 60  # 留出空间显示文件名
                    frame_width = int(frame_height * width / height)
                    if frame_width > preview.width() - 20:
                        frame_width = preview.width() - 20
                        frame_height = int(frame_width * height / width)
                    
                    # 转换帧为 QPixmap
                    bytes_per_line = 3 * width
                    q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    frame_pixmap = QPixmap.fromImage(q_img).scaled(
                        frame_width, frame_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    
                    # 绘制视频帧
                    frame_x = (preview.width() - frame_width) // 2
                    frame_y = (preview.height() - frame_height - 30) // 2
                    painter.drawPixmap(frame_x, frame_y, frame_pixmap)
                    
                    # 添加半透明遮罩
                    painter.setBrush(QColor(0, 0, 0, 100))
                    painter.drawRect(frame_x, frame_y, frame_width, frame_height)
                    
                    # 绘制播放图标（调整大小和位置）
                    play_icon = qta.icon(
                        'fa5s.play-circle',
                        color='white',
                        opacity=0.9
                    ).pixmap(QSize(32, 32))
                    
                    # 将播放图标放在视频帧的右下角
                    margin = 10
                    play_x = frame_x + frame_width - play_icon.width() - margin
                    play_y = frame_y + frame_height - play_icon.height() - margin
                    painter.drawPixmap(play_x, play_y, play_icon)
                    
                    # 绘制文件名（移到底部）
                    file_name = os.path.basename(media_path)
                    if len(file_name) > 30:
                        file_name = file_name[:27] + "..."
                    
                    painter.setPen(QColor('#666666'))
                    font = painter.font()
                    font.setPointSize(10)
                    painter.setFont(font)
                    
                    text_rect = painter.fontMetrics().boundingRect(file_name)
                    text_x = (preview.width() - text_rect.width()) // 2
                    text_y = frame_y + frame_height + 20  # 调整文件名位置
                    painter.drawText(text_x, text_y, file_name)
                    
                    painter.end()
                    self.drop_area.update_preview(preview)
                else:
                    # 如果无法获取视频帧，显示默认图标
                    self._show_default_video_preview(media_path)
            except Exception as e:
                print(f"Error generating video preview: {e}")
                self._show_default_video_preview(media_path)
            
            # 预加载视频但不显示
            if not hasattr(self, 'media_player'):
                self.media_player = QMediaPlayer()
            self.media_player.setSource(QUrl.fromLocalFile(media_path))
    
    def _show_default_video_preview(self, media_path):
        """显示默认的视频预览"""
        preview = QPixmap(self.drop_area.width() - 40, self.drop_area.height() - 40)
        preview.fill(Qt.transparent)
        
        painter = QPainter(preview)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        painter.setBrush(QColor('#F5F5F7'))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, preview.width(), preview.height(), 8, 8)
        
        # 绘制视频图标
        video_icon = qta.icon('fa5s.film', color='#666666').pixmap(QSize(64, 64))
        icon_x = (preview.width() - video_icon.width()) // 2
        icon_y = (preview.height() - video_icon.height()) // 2 - 20
        painter.drawPixmap(icon_x, icon_y, video_icon)
        
        # 绘制文件名
        file_name = os.path.basename(media_path)
        if len(file_name) > 30:
            file_name = file_name[:27] + "..."
        
        painter.setPen(QColor('#666666'))
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        
        text_rect = painter.fontMetrics().boundingRect(file_name)
        text_x = (preview.width() - text_rect.width()) // 2
        text_y = icon_y + video_icon.height() + 20
        painter.drawText(text_x, text_y, file_name)
        
        painter.end()
        self.drop_area.update_preview(preview)
    
    def choose_media_file(self):
        """选择媒体文件"""
        file_filter = "图片文件 (*.jpg *.jpeg *.png *.bmp);;视频文件 (*.mp4 *.avi *.mkv)" if self.image_radio.isChecked() else "视频文件 (*.mp4 *.avi *.mkv);;图片文件 (*.jpg *.jpeg *.png *.bmp)"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择媒体文件",
            "",
            file_filter
        )
        
        if file_path:
            self.handle_dropped_file(file_path)
    
    def check_file_type(self, file_path):
        """检查文件类型是否匹配当前模式"""
        ext = os.path.splitext(file_path)[1].lower()
        if self.image_radio.isChecked():
            return ext in ['.jpg', '.jpeg', '.png', '.bmp']
        else:
            return ext in ['.mp4', '.avi', '.mkv'] 