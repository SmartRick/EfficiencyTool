from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QColorDialog, QSpinBox, QGroupBox,
    QSlider, QComboBox, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase
from utils.config import Config
from utils.style import StyleManager
import qtawesome as qta
import os
from widgets.markdown_viewer import MarkdownViewer

class ColorButton(QPushButton):
    """颜色选择按钮"""
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
        self.color = QColor(color)
        self.update_style()
    
    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color.name(QColor.HexArgb)};
                border: 1px solid #E5E5E5;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 1px solid #007AFF;
            }}
        """)
    
    def get_color(self):
        return self.color.name(QColor.HexArgb)

class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.style_manager = StyleManager()
        
        self.setWindowTitle("设置")
        self.setMinimumSize(600, 500)  # 增加窗口大小
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标签页
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E5E5E5;
                border-radius: 6px;
                background: white;
            }
            QTabBar::tab {
                background: #F5F5F7;
                border: 1px solid #E5E5E5;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
            }
        """)
        
        # 添加设置标签页
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setContentsMargins(16, 16, 16, 16)
        
        # 将原有的设置内容移动到设置标签页
        countdown_group = self.create_countdown_group()
        settings_layout.addWidget(countdown_group)
        settings_layout.addStretch()
        
        # 添加关于标签页
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setContentsMargins(16, 16, 16, 16)
        
        # 创建 Markdown 查看器
        self.markdown_viewer = MarkdownViewer()
        about_layout.addWidget(self.markdown_viewer)
        
        # 加载 README.md 内容
        try:
            # 尝试多个可能的路径
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md'),  # src 目录上层
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'README.md'),  # 项目根目录
                'README.md'  # 当前目录
            ]
            
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'ascii']
            readme_content = None
            
            for path in possible_paths:
                if os.path.exists(path):
                    for encoding in encodings:
                        try:
                            with open(path, 'r', encoding=encoding) as f:
                                readme_content = f.read()
                            break
                        except UnicodeDecodeError:
                            continue
                    if readme_content:
                        break
            
            if readme_content:
                self.markdown_viewer.set_markdown(readme_content)
            else:
                self.markdown_viewer.set_markdown("""# 休息提醒

这是一个帮助您保持健康工作节奏的小工具。

## 主要功能

- 自定义工作和休息时间
- 支持图片和视频屏保
- 友好的提醒方式
- 多屏幕支持

详细说明文件未找到。请访问项目主页了解更多信息。
""")
        except Exception as e:
            self.markdown_viewer.set_markdown(f"# 错误\n\n加载项目说明失败：{str(e)}")
        
        # 添加标签页
        tab_widget.addTab(settings_tab, "设置")
        tab_widget.addTab(about_tab, "关于")
        
        # 按钮区域
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.setFixedWidth(80)
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("取消")
        cancel_button.setFixedWidth(80)
        cancel_button.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        # 添加到主布局
        layout.addWidget(tab_widget)
        layout.addLayout(button_layout)
        
        # 设置样式
        self.setStyleSheet(self._get_style())
    
    def create_countdown_group(self):
        """创建倒计时设置组"""
        # 倒计时样式设置组
        countdown_group = QGroupBox("倒计时样式")
        countdown_layout = QVBoxLayout(countdown_group)
        countdown_layout.setSpacing(16)
        countdown_layout.setContentsMargins(16, 24, 16, 16)
        
        # 字体选择
        font_family_layout = QHBoxLayout()
        font_family_label = QLabel("字体")
        self.font_family_combo = QComboBox()
        self.font_family_combo.setFixedWidth(200)
        
        # 获取系统字体列表
        font_db = QFontDatabase()
        font_families = font_db.families()
        
        # 添加常用字体到前面
        preferred_fonts = [
            "SF Pro Display",
            "Microsoft YaHei",
            "Arial",
            "Helvetica Neue",
            "PingFang SC",
            "-apple-system"
        ]
        
        added_fonts = set()
        
        # 首先添加首选字体
        for font in preferred_fonts:
            if font in font_families and font not in added_fonts:
                self.font_family_combo.addItem(font)
                added_fonts.add(font)
        
        # 如果有首选字体被添加，添加分隔符
        if added_fonts:
            self.font_family_combo.insertSeparator(len(added_fonts))
        
        # 添加其他系统字体
        for font in font_families:
            if font not in added_fonts:
                self.font_family_combo.addItem(font)
        
        self.font_family_combo.currentTextChanged.connect(self.preview_font)
        
        font_family_layout.addWidget(font_family_label)
        font_family_layout.addWidget(self.font_family_combo)
        font_family_layout.addStretch()
        
        # 字体大小设置
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("字体大小")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(12, 72)
        self.font_size_spin.setSuffix(" px")
        self.font_size_spin.valueChanged.connect(self.preview_font_size)
        
        # 预览标签
        self.font_preview = QLabel("88:88")
        self.font_preview.setAlignment(Qt.AlignCenter)
        self.font_preview.setFixedSize(120, 60)
        self.font_preview.setStyleSheet("""
            background: #F5F5F7;
            border-radius: 6px;
        """)
        
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(self.font_size_spin)
        font_size_layout.addStretch()
        font_size_layout.addWidget(self.font_preview)
        
        # 字体颜色设置
        color_layout = QHBoxLayout()
        color_label = QLabel("字体颜色")
        self.color_button = ColorButton('rgba(0, 122, 255, 0.8)')
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        
        # 透明度设置
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("透明度")
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setFixedWidth(120)
        self.opacity_value = QLabel("80%")
        self.opacity_value.setFixedWidth(40)
        
        self.opacity_slider.valueChanged.connect(self.update_opacity_label)
        
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_value)
        opacity_layout.addStretch()
        
        # 添加到倒计时布局
        countdown_layout.addLayout(font_family_layout)
        countdown_layout.addLayout(font_size_layout)
        countdown_layout.addLayout(color_layout)
        countdown_layout.addLayout(opacity_layout)
        
        return countdown_group
    
    def _get_style(self):
        """获取样式表"""
        return """
            QWidget {
                font-family: "SF Pro Display", -apple-system, "Microsoft YaHei";
            }
            QGroupBox {
                font-weight: 500;
                border: 1px solid #E5E5E5;
                border-radius: 6px;
                margin-top: 12px;
                background: white;
            }
            QGroupBox::title {
                color: #333333;
                padding: 0 8px;
                background: white;
            }
            QLabel {
                color: #333333;
                font-size: 13px;
            }
            QPushButton {
                background: #F5F5F7;
                border: 1px solid #E5E5E5;
                border-radius: 4px;
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
            QSpinBox {
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                padding: 4px;
                min-width: 80px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #E5E5E5;
                height: 4px;
                border-radius: 2px;
                background: #F5F5F7;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #007AFF;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #F0F9FF;
            }
            QComboBox {
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                padding: 4px 8px;
                background: white;
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: #007AFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(assets/icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                background: white;
                selection-background-color: #F0F9FF;
            }
        """
    
    def load_settings(self):
        """加载当前设置"""
        # 加载字体
        font_family = self.config.get('countdown.font_family', 'SF Pro Display')
        index = self.font_family_combo.findText(font_family)
        if index >= 0:
            self.font_family_combo.setCurrentIndex(index)
        
        # 加载字体大小
        font_size = self.config.get('countdown.font_size', 48)
        self.font_size_spin.setValue(font_size)
        self.preview_font_size(font_size)
        
        # 加载颜色
        color = self.config.get('countdown.color', 'rgba(0, 122, 255, 0.8)')
        self.color_button.color = QColor(color)
        self.color_button.update_style()
        self.preview_color()
        
        # 加载透明度
        opacity = self.config.get('countdown.opacity', 0.8)
        self.opacity_slider.setValue(int(opacity * 100))
    
    def preview_font(self, family):
        """预览字体"""
        current_font = self.font_preview.font()
        new_font = QFont(family, current_font.pointSize(), QFont.Bold)
        self.font_preview.setFont(new_font)
    
    def preview_font_size(self, size):
        """预览字体大小"""
        current_font = self.font_preview.font()
        current_font.setPointSize(size)
        self.font_preview.setFont(current_font)
    
    def preview_color(self):
        """预览字体颜色"""
        self.font_preview.setStyleSheet(f"""
            background: #F5F5F7;
            border-radius: 6px;
            color: {self.color_button.get_color()};
        """)
    
    def choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor(
            self.color_button.color,
            self,
            "选择颜色",
            QColorDialog.ShowAlphaChannel
        )
        if color.isValid():
            self.color_button.color = color
            self.color_button.update_style()
            self.preview_color()
    
    def update_opacity_label(self, value):
        """更新透明度标签"""
        self.opacity_value.setText(f"{value}%")
    
    def save_settings(self):
        """保存设置"""
        try:
            # 保存字体
            self.config.set('countdown.font_family', self.font_family_combo.currentText())
            
            # 保存字体大小
            self.config.set('countdown.font_size', self.font_size_spin.value())
            
            # 保存颜色
            self.config.set('countdown.color', self.color_button.get_color())
            
            # 保存透明度
            self.config.set('countdown.opacity', self.opacity_slider.value() / 100)
            
            # 关闭窗口
            self.close()
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "保存失败", f"保存设置时出错：{str(e)}") 