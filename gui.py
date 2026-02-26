#coding=utf-8
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyautogui
import pyperclip
import time
import threading
import json
import os
from pynput import keyboard
from constants import *
from screenshot import SnippingTool

class PictureRPA_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Picture RPA v3.0 - Logic & Snip")
        self.root.geometry("800x700")
        self.root.configure(bg=COLOR_BG_CREAM)

        # 存储指令序列
        self.commands = []
        self.is_running = False

        # 按键监听器
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        # 使用 constants 中的映射
        self.cmd_types = CMD_TYPES
        self.rev_cmd_types = REV_CMD_TYPES

        self.setup_styles()
        self.build_ui()
        self.log("RPA 等待中", "info")
        self.log("提示: 运行中可按ESC键紧急停止", "warn")

    def log(self, msg, tag=""):
        """向GUI日志区添加信息"""
        t = time.strftime("%H:%M:%S", time.localtime())
        self.log_text.insert(tk.END, f"[{t}] {msg}\n", tag)
        self.log_text.see(tk.END)
        print(f"[{t}] {msg}")

    def on_press(self, key):
        """监听全局键盘按键"""
        if key == keyboard.Key.esc:
            if self.is_running:
                self.log("ESC触发，已停止程序", "err")
                self.stop_run()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TTreeview", background="white", fieldbackground="white", foreground="black")
        style.map("TTreeview", background=[('selected', COLOR_SLATE_PURPLE)])
        style.configure("TLabel", background=COLOR_BG_CREAM, foreground="#333333", font=("Microsoft YaHei", 10))
        style.configure("TButton", font=("Microsoft YaHei", 10), background=COLOR_PINK_ROSE, foreground="black")
        style.map("TButton", background=[('active', COLOR_SLATE_PURPLE), ('active', 'white')])

    def build_ui(self):
        frame_top = tk.Frame(self.root, bg=COLOR_BG_CREAM, pady=10, padx=10)
        frame_top.pack(fill=tk.X)

        ttk.Label(frame_top, text="操作类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_type = ttk.Combobox(frame_top, values=list(self.cmd_types.keys()), state="readonly", width=18)
        self.combo_type.current(0)
        self.combo_type.grid(row=0, column=1, padx=5, pady=5)
        self.combo_type.bind("<<ComboboxSelected>>", self.on_type_change)

        ttk.Label(frame_top, text="内容/路径:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.entry_value = tk.Entry(frame_top, width=30)
        self.entry_value.grid(row=0, column=3, padx=5, pady=5)

        self.btn_snip = tk.Button(frame_top, text="✂截图保存", command=self.snip_image, bg="white", relief=tk.FLAT)
        self.btn_snip.grid(row=0, column=4, padx=5, pady=5)

        self.btn_browse = tk.Button(frame_top, text="浏览图片", command=self.browse_image, bg=COLOR_PINK_ROSE, relief=tk.FLAT)
        self.btn_browse.grid(row=0, column=5, padx=5, pady=5)

        self.lbl_retry = ttk.Label(frame_top, text="重试次数:")
        self.lbl_retry.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_retry = tk.Entry(frame_top, width=21)
        self.entry_retry.insert(0, "1")
        self.entry_retry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_top, text="匹配精度:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.entry_conf = tk.Entry(frame_top, width=10)
        self.entry_conf.insert(0, "0.9")
        self.entry_conf.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

        btn_add = tk.Button(frame_top, text="➕ 添加到流程", command=self.add_command, bg=COLOR_SLATE_PURPLE, fg="white", relief=tk.FLAT, font=("Microsoft YaHei", 10, "bold"))
        btn_add.grid(row=1, column=4, columnspan=2, sticky=tk.E, padx=5, pady=5)

        frame_mid = tk.Frame(self.root, bg=COLOR_BG_CREAM, padx=10)
        frame_mid.pack(fill=tk.BOTH, expand=True)

        columns = ("step", "type", "value", "retry")
        self.tree = ttk.Treeview(frame_mid, columns=columns, show="headings", height=12)
        self.tree.heading("step", text="步骤")
        self.tree.heading("type", text="操作类型")
        self.tree.heading("value", text="内容 / 路径")
        self.tree.heading("retry", text="重试 / 跳转步")
        self.tree.column("step", width=50, anchor=tk.CENTER)
        self.tree.column("type", width=150, anchor=tk.CENTER)
        self.tree.column("value", width=380, anchor=tk.W)
        self.tree.column("retry", width=100, anchor=tk.CENTER)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.tree.bind("<ButtonRelease-1>", self.on_drag_stop)

        scrollbar = ttk.Scrollbar(frame_mid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(self.root, height=8, bg="#1e1e1e", fg="#d1d5db", font=("Consolas", 9), padx=5, pady=5)
        self.log_text.pack(fill=tk.BOTH, side=tk.BOTTOM, padx=10, pady=5)
        self.log_text.tag_config("info", foreground="#10b981")
        self.log_text.tag_config("warn", foreground="#f59e0b")
        self.log_text.tag_config("err", foreground="#ef4444")

        frame_bottom = tk.Frame(self.root, bg=COLOR_BG_CREAM, pady=5)
        frame_bottom.pack(fill=tk.X)
        btn_del = tk.Button(frame_bottom, text="Delete删除", command=self.delete_command, bg="#fca5a5", relief=tk.FLAT)
        btn_del.pack(side=tk.LEFT, padx=10)
        ttk.Label(frame_bottom, text="循环次数:").pack(side=tk.LEFT, padx=2)
        self.entry_loop_count = tk.Entry(frame_bottom, width=5)
        self.entry_loop_count.insert(0, "1")
        self.entry_loop_count.pack(side=tk.LEFT, padx=5)
        btn_save = tk.Button(frame_bottom, text="Save保存", command=self.save_workflow, bg="white", relief=tk.FLAT)
        btn_save.pack(side=tk.LEFT, padx=5)
        btn_load = tk.Button(frame_bottom, text="Load加载", command=self.load_workflow, bg="white", relief=tk.FLAT)
        btn_load.pack(side=tk.LEFT, padx=5)
        self.btn_stop = tk.Button(frame_bottom, text="Stop停止", command=self.stop_run, bg="#fca5a5", relief=tk.FLAT, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.RIGHT, padx=10)
        self.btn_run_loop = tk.Button(frame_bottom, text="Infinity循环", command=lambda: self.start_run(loop=True), bg=COLOR_SLATE_PURPLE, fg="white", relief=tk.FLAT)
        self.btn_run_loop.pack(side=tk.RIGHT, padx=5)
        self.btn_run_once = tk.Button(frame_bottom, text="Once执行", command=lambda: self.start_run(loop=False), bg=COLOR_PINK_ROSE, relief=tk.FLAT)
        self.btn_run_once.pack(side=tk.RIGHT, padx=5)

    def snip_image(self):
        self.root.iconify()
        time.sleep(0.3)
        SnippingTool(self.root, self.save_snip)

    def save_snip(self, img):
        self.root.deiconify()
        if not os.path.exists("snips"): os.makedirs("snips")

        name_win = tk.Toplevel(self.root)
        name_win.title("命名截图")
        name_win.geometry("350x150")
        name_win.resizable(False, False)
        name_win.transient(self.root)
        name_win.grab_set()

        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        name_win.geometry(f"+{main_x + 200}+{main_y + 200}")

        tk.Label(name_win, text="请输入英文文件名 (留空则使用默认):", font=("Microsoft YaHei", 10)).pack(pady=15)
        
        name_entry = tk.Entry(name_win, width=35, font=("Microsoft YaHei", 10))
        name_entry.pack(pady=5, padx=20)
        name_entry.focus_set() # 自动聚焦
        
        self._custom_filename_result = None
        
        def confirm(event=None):
            self._custom_filename_result = name_entry.get().strip()
            name_win.destroy()

        name_entry.bind("<Return>", confirm)
        
        btn_confirm = tk.Button(name_win, text="确定 (Enter)", command=confirm, bg=COLOR_SLATE_PURPLE, fg="white", relief=tk.FLAT, width=15)
        btn_confirm.pack(pady=15)
        
        self.root.wait_window(name_win)
        
        custom_name = self._custom_filename_result
        if custom_name:
            if not custom_name.endswith(".png"): custom_name += ".png"
            filename = f"snips/{custom_name}"
            if os.path.exists(filename):
                filename = f"snips/{int(time.time())}_{custom_name}"
        else:
            filename = f"snips/snip_{int(time.time())}.png"
            
        img.save(filename)
        self.entry_value.delete(0, tk.END)
        self.entry_value.insert(0, os.path.abspath(filename))
        self.log(f"截图已保存: {filename}", "info")

    def on_drag_start(self, event):
        self._drag_item = self.tree.identify_row(event.y)

    def on_drag_stop(self, event):
        if not hasattr(self, "_drag_item") or not self._drag_item: return
        target_item = self.tree.identify_row(event.y)
        if not target_item or target_item == self._drag_item: return
        source_idx, target_idx = self.tree.index(self._drag_item), self.tree.index(target_item)
        cmd = self.commands.pop(source_idx)
        self.commands.insert(target_idx, cmd)
        self.tree.move(self._drag_item, "", target_idx)
        self.refresh_steps()

    def refresh_steps(self):
        for i, item in enumerate(self.tree.get_children()):
            vals = list(self.tree.item(item, "values"))
            vals[0] = i + 1
            self.tree.item(item, values=vals)

    def on_type_change(self, event):
        selected = self.combo_type.get()
        cmd_val = self.cmd_types[selected]
        self.entry_value.delete(0, tk.END)
        if cmd_val in [1.0, 2.0, 3.0]:
            self.lbl_retry.config(text="重试次数:")
            self.btn_browse.config(state=tk.NORMAL)
            self.btn_snip.config(state=tk.NORMAL)
            self.entry_retry.config(state=tk.NORMAL)
        elif cmd_val in [8.0, 9.0]:
            self.lbl_retry.config(text="跳转到步:")
            self.btn_browse.config(state=tk.NORMAL)
            self.btn_snip.config(state=tk.NORMAL)
            self.entry_retry.config(state=tk.NORMAL)
        elif cmd_val == 10.0:
            self.entry_value.insert(0, "End")
            self.btn_browse.config(state=tk.DISABLED)
            self.btn_snip.config(state=tk.DISABLED)
            self.entry_retry.config(state=tk.DISABLED)
        elif cmd_val == 7.0:
            self.entry_value.insert(0, "ctrl+v")
            self.btn_browse.config(state=tk.DISABLED)
            self.btn_snip.config(state=tk.DISABLED)
            self.entry_retry.config(state=tk.DISABLED)
        else:
            self.lbl_retry.config(text="重试次数:")
            self.btn_browse.config(state=tk.DISABLED)
            self.btn_snip.config(state=tk.DISABLED)
            self.entry_retry.config(state=tk.DISABLED)

    def browse_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if filepath:
            self.entry_value.delete(0, tk.END)
            self.entry_value.insert(0, filepath)

    def add_command(self):
        name = self.combo_type.get()
        val, v_raw, r_raw = self.cmd_types[name], self.entry_value.get().strip(), self.entry_retry.get().strip()
        try:
            r_val = int(r_raw) if r_raw else 0
        except: r_val = 0
        self.commands.append({"type": val, "value": v_raw, "retry": r_val})
        self.tree.insert("", tk.END, values=(len(self.commands), name, v_raw, r_val))

    def delete_command(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        self.tree.delete(sel[0])
        self.commands.pop(idx)
        self.refresh_steps()

    def save_workflow(self):
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if path:
            with open(path, 'w', encoding='utf-8') as f: json.dump(self.commands, f, indent=4, ensure_ascii=False)

    def load_workflow(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path, 'r', encoding='utf-8') as f: data = json.load(f)
            self.commands.clear()
            for i in self.tree.get_children(): self.tree.delete(i)
            for i, cmd in enumerate(data):
                self.commands.append(cmd)
                self.tree.insert("", tk.END, values=(i+1, self.rev_cmd_types.get(cmd["type"], "Unknown"), cmd["value"], cmd["retry"]))

    def mouseClick(self, clickTimes, lOrR, img, retry, conf=0.9):
        if not os.path.exists(img): 
            self.log(f"错误: 找不到文件 {img}", "err")
            return False
        
        # 重试
        max_attempts = 5 if retry <= 1 else int(retry)
        if retry == -1: max_attempts = 999999
        
        self.log(f"正在寻找: {os.path.basename(img)} (精度:{conf})", "info")
        
        for i in range(max_attempts):
            if not self.is_running: break
            try:
                loc = pyautogui.locateCenterOnScreen(img, confidence=conf)
                if loc:
                    pyautogui.click(loc.x, loc.y, clicks=clickTimes, interval=0.2, button=lOrR)
                    return True
            except: pass
            time.sleep(0.1)
            
        return False

    def execute_workflow(self):
        try: conf = float(self.entry_conf.get())
        except: conf = 0.9
        
        i = 0
        while i < len(self.commands) and self.is_running:
            cmd = self.commands[i]
            c_type, c_val, c_ret = cmd["type"], cmd["value"], cmd["retry"]

            try:
                item_id = self.tree.get_children()[i]
                self.tree.selection_set(item_id)
                self.tree.see(item_id)
            except: pass

            next_step = i + 1

            if c_type in [1.0, 2.0, 3.0]:
                clicks, btn = (1, "left") if c_type==1.0 else (2, "left") if c_type==2.0 else (1, "right")
                if self.mouseClick(clicks, btn, str(c_val), c_ret, conf):
                    self.log(f"Step {i+1}: 已执行找图点击", "info")
                else:
                    self.log(f"Step {i+1}: 未找到图 {os.path.basename(str(c_val))}", "warn")
            elif c_type == 4.0:
                pyperclip.copy(str(c_val)); pyautogui.hotkey('ctrl', 'v'); time.sleep(0.5)
            elif c_type == 5.0:
                t_end = time.time() + float(c_val)
                while time.time() < t_end and self.is_running: time.sleep(0.1)
            elif c_type == 6.0:
                pyautogui.scroll(int(c_val))
            elif c_type == 7.0:
                pyautogui.hotkey(*[k.strip() for k in str(c_val).lower().split('+')])
            elif c_type == 8.0: # 跳转
                if pyautogui.locateOnScreen(str(c_val), confidence=conf):
                    self.log(f"找到图，跳转到第 {c_ret} 步", "info")
                    next_step = int(c_ret) - 1
            elif c_type == 9.0: # 跳转
                if not pyautogui.locateOnScreen(str(c_val), confidence=conf):
                    self.log(f"未找到图，跳转到第 {c_ret} 步", "info")
                    next_step = int(c_ret) - 1
            elif c_type == 10.0:
                self.log("流程强制结束", "err")
                self.is_running = False
                break
            
            i = next_step

    def worker_thread(self, loop):
        try:
            if loop:
                while self.is_running: self.execute_workflow()
            else:
                try: count = int(self.entry_loop_count.get())
                except: count = 1
                for _ in range(count):
                    if not self.is_running: break
                    self.execute_workflow()
        finally: self.stop_run()

    def start_run(self, loop=False):
        if not self.commands: return
        self.is_running = True
        self.btn_run_once.config(state=tk.DISABLED); self.btn_run_loop.config(state=tk.DISABLED); self.btn_stop.config(state=tk.NORMAL)
        threading.Thread(target=self.worker_thread, args=(loop,), daemon=True).start()

    def stop_run(self):
        self.is_running = False
        self.btn_run_once.config(state=tk.NORMAL); self.btn_run_loop.config(state=tk.NORMAL); self.btn_stop.config(state=tk.DISABLED)
