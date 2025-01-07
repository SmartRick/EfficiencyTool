<div align="center">

# 休息提醒工具 (EfficiencyTool)

[![GitHub stars](https://img.shields.io/github/stars/SmartRick/EfficiencyTool.svg?style=flat&logo=github)](https://github.com/SmartRick/EfficiencyTool/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/SmartRick/EfficiencyTool.svg?style=flat&logo=github)](https://github.com/SmartRick/EfficiencyTool/network/members)
[![GitHub issues](https://img.shields.io/github/issues/SmartRick/EfficiencyTool.svg?style=flat&logo=github)](https://github.com/SmartRick/EfficiencyTool/issues)
[![GitHub license](https://img.shields.io/github/license/SmartRick/EfficiencyTool.svg?style=flat&logo=github)](https://github.com/SmartRick/EfficiencyTool/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![QT Version](https://img.shields.io/badge/Qt-6.0+-green.svg?style=flat&logo=qt&logoColor=white)](https://www.qt.io)

一个基于 PySide6 开发的优雅休息提醒工具，帮助你保持健康的工作节奏。

[English](./README_EN.md) | 简体中文

</div>

## ✨ 特性

- 🎯 自定义工作/休息时间
- 🖼️ 支持图片/视频屏保
- 🔔 系统托盘通知
- 💻 多屏幕支持
- 🎨 现代化 UI 设计
- ⌨️ 全局快捷键支持
- 🌙 优雅的过渡动画

## 🖥️ 预览

<div align="center">
<img src="docs/images/preview.png" alt="预览图" width="600"/>
</div>

## 🚀 快速开始

### 环境要求

- Python 3.8+
- PySide6
- OpenCV-Python (可选，用于视频预览)

### 安装

```
</div>

```bash
# 克隆项目
git clone https://github.com/SmartRick/EfficiencyTool.git

# 进入项目目录
cd EfficiencyTool

# 安装依赖
pip install -r requirements.txt

# 运行程序
python src/main.py
```

## 🛠️ 配置说明

配置文件位于 `src/config/style.yaml`，你可以自定义：

- 工作/休息时间
- 屏保媒体类型和路径
- 快捷键
- UI 样式
- 等等...

## 🔧 主要功能

### 1. 工作计时
- 自定义工作时长
- 倒计时显示
- 托盘状态提示

### 2. 休息提醒
- 自定义休息时长
- 全屏屏保显示
- 支持图片/视频

### 3. 屏保设置
- 支持拖放添加媒体
- 实时预览
- 多种显示模式

## 📝 待办事项

- [ ] 添加番茄钟模式
- [ ] 支持自定义主题
- [ ] 添加数据统计
- [ ] 优化多显示器支持
- [ ] 添加插件系统

## 🤝 贡献指南

欢迎提交 Pull Request 或 Issue！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📄 开源协议

本项目基于 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 🙏 鸣谢

- [PySide6](https://doc.qt.io/qtforpython-6/) - Qt for Python
- [OpenCV-Python](https://github.com/opencv/opencv-python) - 视频处理支持
- [qtawesome](https://github.com/spyder-ide/qtawesome) - 图标支持

## 🌟 Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=SmartRick/EfficiencyTool&type=Date)](https://star-history.com/#SmartRick/EfficiencyTool&Date)

---

> 如果这个项目对你有帮助，欢迎点个 Star ⭐️