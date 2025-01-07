from PySide6.QtWidgets import QTextBrowser
from PySide6.QtCore import Qt
import markdown
import os

class MarkdownViewer(QTextBrowser):
    """Markdown 查看器组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        self.setStyleSheet("""
            QTextBrowser {
                background: white;
                border: none;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        
        # 设置 CSS 样式
        self.document().setDefaultStyleSheet("""
            h1 { font-size: 24px; margin-top: 16px; margin-bottom: 16px; }
            h2 { font-size: 20px; margin-top: 14px; margin-bottom: 14px; }
            h3 { font-size: 16px; margin-top: 12px; margin-bottom: 12px; }
            p { margin: 12px 0; }
            code { 
                background: #F5F5F7; 
                padding: 2px 4px; 
                border-radius: 4px;
                font-family: "SF Mono", Consolas, "Liberation Mono", Menlo, Courier, monospace;
            }
            pre {
                background: #F5F5F7;
                padding: 12px;
                border-radius: 6px;
                margin: 12px 0;
            }
            pre code {
                background: transparent;
                padding: 0;
            }
            ul, ol {
                margin: 12px 0;
                padding-left: 24px;
            }
            li { margin: 6px 0; }
            a { color: #007AFF; text-decoration: none; }
            a:hover { text-decoration: underline; }
            blockquote {
                margin: 12px 0;
                padding: 8px 12px;
                border-left: 4px solid #E5E5E5;
                background: #F5F5F7;
            }
        """)
    
    def set_markdown(self, text):
        """设置并渲染 Markdown 内容"""
        html = markdown.markdown(
            text,
            extensions=['fenced_code', 'tables', 'nl2br']
        )
        self.setHtml(html) 