from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt, QSize
import qtawesome as qta

class SidebarButton(QPushButton):
    """侧边栏按钮"""
    def __init__(self, icon_name, text, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedHeight(40)
        
        # 设置图标
        self.setIcon(qta.icon(icon_name, color='#666666'))
        self.setIconSize(QSize(16, 16))
        self.setText(text)
        
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                text-align: left;
                color: #666666;
                font-size: 13px;
                background: transparent;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.05);
            }
            QPushButton:checked {
                background: #F0F9FF;
                color: #007AFF;
            }
            QPushButton:checked:hover {
                background: #E5F3FF;
            }
        """)

class Sidebar(QWidget):
    """侧边栏导航"""
    pageChanged = Signal(str)  # 页面切换信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(180)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # 创建导航按钮
        self.buttons = {}
        
        # 休息提醒
        break_btn = SidebarButton('fa5s.coffee', '休息提醒')
        self.buttons['break'] = break_btn
        
        # 待办事项
        todo_btn = SidebarButton('fa5s.tasks', '待办事项')
        self.buttons['todo'] = todo_btn
        
        # 笔记
        notes_btn = SidebarButton('fa5s.sticky-note', '笔记')
        self.buttons['notes'] = notes_btn
        
        # 设置
        settings_btn = SidebarButton('fa5s.cog', '设置')
        self.buttons['settings'] = settings_btn
        
        # 添加按钮到布局
        layout.addWidget(break_btn)
        layout.addWidget(todo_btn)
        layout.addWidget(notes_btn)
        layout.addStretch()
        layout.addWidget(settings_btn)
        
        # 连接信号
        for page_id, btn in self.buttons.items():
            btn.clicked.connect(lambda checked, pid=page_id: self.on_button_clicked(pid))
        
        # 设置默认选中
        break_btn.setChecked(True)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background: white;
                border-right: 1px solid #E5E5E5;
            }
        """)
    
    def on_button_clicked(self, page_id):
        """处理按钮点击"""
        # 更新按钮状态
        for pid, btn in self.buttons.items():
            btn.setChecked(pid == page_id)
        
        # 发送页面切换信号
        self.pageChanged.emit(page_id) 