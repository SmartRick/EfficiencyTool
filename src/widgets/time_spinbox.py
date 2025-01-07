from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal
import qtawesome as qta

class TimeSpinBox(QWidget):
    """时间调节控件"""
    valueChanged = Signal(int)
    
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
        decrease_btn = QPushButton()
        decrease_btn.setIcon(qta.icon('fa5s.minus', color='#666666'))
        decrease_btn.clicked.connect(self.decrease)
        
        # 数值显示
        self.value_label = QLabel(f"{self.value}分钟")
        self.value_label.setStyleSheet("color: #333333;")
        
        # 增加按钮
        increase_btn = QPushButton()
        increase_btn.setIcon(qta.icon('fa5s.plus', color='#666666'))
        increase_btn.clicked.connect(self.increase)
        
        # 设置按钮样式
        for btn in [decrease_btn, increase_btn]:
            btn.setFixedSize(24, 24)
            btn.setStyleSheet("""
                QPushButton {
                    background: #F5F5F7;
                    border: 1px solid #E5E5E5;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background: #EAEAEB;
                }
                QPushButton:pressed {
                    background: #DCDCDC;
                }
            """)
        
        layout.addWidget(decrease_btn)
        layout.addWidget(self.value_label)
        layout.addWidget(increase_btn)
    
    def increase(self):
        if self.value < self.max_value:
            self.value += 1
            self.update_display()
            self.valueChanged.emit(self.value)
    
    def decrease(self):
        if self.value > self.min_value:
            self.value -= 1
            self.update_display()
            self.valueChanged.emit(self.value)
    
    def update_display(self):
        self.value_label.setText(f"{self.value}分钟") 