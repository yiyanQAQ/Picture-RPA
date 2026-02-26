import tkinter as tk
from PIL import ImageGrab
import os
import time

class SnippingTool:
    """截图工具"""
    def __init__(self, master, callback):
        self.master = master
        self.callback = callback
        self.snip_win = tk.Toplevel(master)
        self.snip_win.attributes("-alpha", 0.3)
        self.snip_win.attributes("-fullscreen", True)
        self.snip_win.attributes("-topmost", True)
        self.snip_win.config(cursor="cross")
        
        self.canvas = tk.Canvas(self.snip_win, cursor="cross", bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_snip_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.snip_win.bind("<Escape>", lambda e: self.snip_win.destroy())

    def on_button_press(self, event):
        self.start_x = self.snip_win.winfo_pointerx()
        self.start_y = self.snip_win.winfo_pointery()
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

    def on_snip_drag(self, event):
        cur_x, cur_y = (self.snip_win.winfo_pointerx(), self.snip_win.winfo_pointery())
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x, end_y = (self.snip_win.winfo_pointerx(), self.snip_win.winfo_pointery())
        self.snip_win.destroy()

        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        if x2 - x1 > 5 and y2 - y1 > 5:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.callback(img)
