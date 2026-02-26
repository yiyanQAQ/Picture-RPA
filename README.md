# Picture RPA v3.0

[中文](#中文) | [English](#english)

---

## 中文

### 简介
基于图像识别的轻量级RPA工具

### 核心功能
- **内置截图工具**
- **图像识别**
- **逻辑控制**
- **流程编辑**

### 目录结构
- `pictureRPA.py`: 主程序
- `snips/`: 截图保存目录

### 运行
1. **配置环境**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **启动程序**:
   ```bash
   python pictureRPA.py
   ```

---

## English

### Introduction
Picture RPA is a lightweight Robotic Process Automation tool based on image recognition. It features a graphical user interface for recording and managing automated workflows, including image-based clicking, text input, hotkey execution, and conditional logic.

### Key Features
- **Built-in Snipping Tool**: Capture screenshots instantly with custom naming and automatic path filling.
- **Image Recognition**: High-precision matching powered by OpenCV with adjustable confidence levels.
- **Logical Flow Control**: Supports conditional branching (If/Goto) based on image detection results.
- **Hotkey Support**: Execute complex keyboard combinations (e.g., `ctrl+v`, `alt+f4`).
- **Workflow Editor**: Reorder steps via drag-and-drop, delete steps, and save/load workflows in JSON format.
- **Emergency Stop**: Global **ESC** key listener to terminate execution immediately.

### Installation
1. **Clone**:
   ```bash
   git clone https://github.com/your-username/picture_RPA.git
   ```
2. **Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Run**:
   ```bash
   python pictureRPA.py
   ```
