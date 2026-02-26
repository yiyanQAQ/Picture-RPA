COLOR_BG_CREAM = "#F3F3F3"
COLOR_PINK_ROSE = "#E1E1E1"
COLOR_SLATE_PURPLE = "#0078D4"

CMD_TYPES = {
    "单击左键 (找图)": 1.0,
    "双击左键 (找图)": 2.0,
    "单击右键 (找图)": 3.0,
    "文本输入 (复制粘贴)": 4.0,
    "等待时长 (秒)": 5.0,
    "鼠标滚轮 (滑动)": 6.0,
    "执行快捷键 (Hotkey)": 7.0,
    "跳转:若找到图 (Goto)": 8.0,
    "跳转:若没找到图 (Goto)": 9.0,
    "结束流程 (Stop)": 10.0
}

REV_CMD_TYPES = {v: k for k, v in CMD_TYPES.items()}
