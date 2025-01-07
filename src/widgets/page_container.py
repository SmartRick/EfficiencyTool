from PySide6.QtWidgets import (
    QStackedWidget, QWidget, QVBoxLayout,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup
from widgets.control_panel import ControlPanel

class PageContainer(QStackedWidget):
    """页面容器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_pages()
        self.current_index = 0
        self.is_animating = False
        
        # 初始化所有页面位置
        for i in range(self.count()):
            self.widget(i).move(0, 0)
    
    def init_pages(self):
        # 休息提醒页面
        break_page = QWidget()
        break_layout = QVBoxLayout(break_page)
        break_layout.setContentsMargins(20, 0, 20, 20)
        
        # 使用滚动区域包装 ControlPanel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        control_panel = ControlPanel()
        control_panel.setMinimumHeight(400)
        control_panel.setMaximumHeight(800)
        
        scroll_area.setWidget(control_panel)
        break_layout.addWidget(scroll_area)
        
        self.addWidget(break_page)
        
        # 其他页面保持类似的布局结构
        for page_name in ['todo', 'notes', 'settings']:
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(20, 0, 20, 20)
            
            content = QWidget()
            content.setMinimumHeight(400)
            content.setMaximumHeight(800)
            
            layout.addWidget(content)
            self.addWidget(page) 
    
    def setCurrentIndex(self, index):
        """重写切换页面方法，添加动画"""
        if self.current_index == index or self.is_animating:
            return
            
        self.is_animating = True
        
        # 获取页面移动方向
        direction = 1 if index > self.current_index else -1
        
        # 获取当前页面和目标页面
        next_page = self.widget(index)
        current_page = self.widget(self.current_index)
        
        # 重置所有页面位置和可见性
        for i in range(self.count()):
            page = self.widget(i)
            if page not in [current_page, next_page]:
                page.hide()
        
        # 准备动画
        next_page.show()
        next_page.raise_()
        offset = self.width() * direction
        next_page.move(offset, 0)
        
        # 创建动画组
        anim_group = QParallelAnimationGroup(self)
        
        # 设置动画参数
        duration = 250  # 稍微加快动画速度
        
        # 当前页面动画
        current_anim = QPropertyAnimation(current_page, b"pos", self)
        current_anim.setStartValue(current_page.pos())
        current_anim.setEndValue(QPoint(-offset, 0))
        current_anim.setDuration(duration)
        current_anim.setEasingCurve(QEasingCurve.InOutQuad)  # 更平滑的缓动
        
        # 下一页动画
        next_anim = QPropertyAnimation(next_page, b"pos", self)
        next_anim.setStartValue(QPoint(offset, 0))
        next_anim.setEndValue(QPoint(0, 0))
        next_anim.setDuration(duration)
        next_anim.setEasingCurve(QEasingCurve.InOutQuad)  # 更平滑的缓动
        
        # 添加动画到组
        anim_group.addAnimation(current_anim)
        anim_group.addAnimation(next_anim)
        
        # 动画完成后的处理
        def on_finished():
            self.is_animating = False
            self.current_index = index
            # 重置其他页面
            for i in range(self.count()):
                page = self.widget(i)
                if page not in [current_page, next_page]:
                    page.move(0, 0)
            super(PageContainer, self).setCurrentIndex(index)
        
        anim_group.finished.connect(on_finished)
        anim_group.start() 