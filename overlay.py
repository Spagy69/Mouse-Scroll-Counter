import tkinter as tk
from tkinter import messagebox, ttk
import ctypes
import platform
import queue
import os
from config import load_config, save_config, get_resource_path

def get_monitors():
    monitors = []
    try:
        def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            monitors.append({
                "left": lprcMonitor.contents.left,
                "top": lprcMonitor.contents.top,
                "right": lprcMonitor.contents.right,
                "bottom": lprcMonitor.contents.bottom,
                "width": abs(lprcMonitor.contents.right - lprcMonitor.contents.left),
                "height": abs(lprcMonitor.contents.bottom - lprcMonitor.contents.top)
            })
            return True

        MONITORENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_double)
        ctypes.windll.user32.EnumDisplayMonitors(0, 0, MONITORENUMPROC(callback), 0)
    except Exception as e:
        print(f"Error getting monitors: {e}")
    return monitors

class Overlay:
    def __init__(self, root, command_queue, input_handler):
        self.root = root
        self.command_queue = command_queue
        self.input_handler = input_handler
        self.root.title("Mouse Scroll Counter Overlay")
        
        self.config = load_config()
        self.load_custom_font()

        # Window constraints
        self.root.overrideredirect(True)  # Remove title bar
        self.root.geometry("200x150")
        
        # Position logic
        self.update_position()
        
        # Always on top
        self.root.attributes("-topmost", True)
        
        # Transparency
        bg_color = "#000001" 
        self.root.config(bg=bg_color)
        if platform.system() == "Windows":
            self.root.attributes("-transparentcolor", bg_color)

        # Labels
        font_name = self.config.get("font_name", "Segoe UI")
        # Fallback if load failed or simple name used
        self.font_style = (font_name, 24, "bold")
        
        # Green (Up)
        self.up_label = tk.Label(self.root, text="0", fg="#00ff00", bg=bg_color, font=self.font_style)
        self.up_label.pack(side="top", pady=(10, 0))
        
        # Separator (White Line)
        self.separator = tk.Frame(self.root, bg="white", height=2, width=100)
        self.separator.pack(side="top", pady=5)

        # Red (Down)
        self.down_label = tk.Label(self.root, text="0", fg="#ff0000", bg=bg_color, font=self.font_style)
        self.down_label.pack(side="top", pady=(0, 10))

        # Click-through (Windows only)
        self.make_click_through()
        
        # Start Polling
        self.poll()

    def load_custom_font(self):
        font_path = self.config.get("font_path", "")
        if font_path:
            abs_font_path = get_resource_path(font_path)
            if os.path.exists(abs_font_path) and platform.system() == "Windows":
                 try:
                     FR_PRIVATE = 0x10
                     ctypes.windll.gdi32.AddFontResourceExW(ctypes.c_wchar_p(abs_font_path), FR_PRIVATE, 0)
                 except Exception as e:
                     print(f"Failed to load font: {e}")

    def update_position(self):
        monitors = get_monitors()
        monitor_index = self.config.get("monitor_index", 0)
        
        # Overlay dimensions
        w = 200
        h = 150
        
        if 0 <= monitor_index < len(monitors):
            m = monitors[monitor_index]
            # Calculate 5% margin
            margin_right = int(m["width"] * 0.05)
            margin_top = int(m["height"] * 0.05)
            
            # Position top-right with margin
            x_pos = m["right"] - w - margin_right
            y_pos = m["top"] + margin_top
        else:
            # Fallback to primary/default tk behavior if index invalid
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            margin_right = int(screen_width * 0.05)
            margin_top = int(screen_height * 0.05)
            
            x_pos = screen_width - w - margin_right
            y_pos = margin_top
            
        self.root.geometry(f"{w}x{h}+{int(x_pos)}+{int(y_pos)}")

    def make_click_through(self):
        if platform.system() == "Windows":
            try:
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
                style = style | 0x00000020 | 0x00080000
                ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            except Exception as e:
                print(f"Failed to set click-through: {e}")

    def update_counts(self, up_count, down_count):
        self.up_label.config(text=str(up_count))
        self.down_label.config(text=str(down_count))
        
    def poll(self):
        # Update counts
        u, d = self.input_handler.get_counts()
        self.update_counts(u, d)
        
        # Check queue
        try:
            while True:
                cmd = self.command_queue.get_nowait()
                if cmd == "settings":
                    self.show_settings()
                elif cmd == "help":
                    self.show_help()
                elif cmd == "quit":
                    self.root.quit()
        except queue.Empty:
            pass
            
        self.root.after(50, self.poll)

    def show_settings(self):
        # Create Toplevel
        top = tk.Toplevel(self.root)
        top.title("Settings")
        top.geometry("300x250")
        
        # Ensure it's not transparent and has decorations
        top.attributes("-alpha", 1.0)
        top.attributes("-topmost", True)
        
        # Center checking
        ws = top.winfo_screenwidth()
        hs = top.winfo_screenheight()
        x = (ws/2) - (150)
        y = (hs/2) - (125)
        top.geometry(f"300x250+{int(x)}+{int(y)}")

        # Reset Key Section
        lbl_reset = tk.Label(top, text="Click below then press key to set Reset Key:")
        lbl_reset.pack(pady=(10, 5))
        
        btn_reset = tk.Button(top, text=f"Current: {self.input_handler.reset_key}")
        btn_reset.pack(pady=5)
        
        # Monitor Section
        lbl_monitor = tk.Label(top, text="Monitor Index:")
        lbl_monitor.pack(pady=(10, 5))
        
        monitors = get_monitors()
        monitor_options = [f"Monitor {i}" for i in range(len(monitors))]
        if not monitor_options:
            monitor_options = ["Monitor 0"]
            
        current_monitor = self.config.get("monitor_index", 0)
        if current_monitor >= len(monitor_options):
            current_monitor = 0
            
        combo_monitor = ttk.Combobox(top, values=monitor_options, state="readonly")
        combo_monitor.current(current_monitor)
        combo_monitor.pack(pady=5)

        def save_settings():
             # Save Monitor
             selected_idx = combo_monitor.current()
             cfg = load_config()
             cfg["monitor_index"] = selected_idx
             save_config(cfg)
             self.config = cfg # Update local config
             self.update_position() # Apply position change immediately
             messagebox.showinfo("Saved", "Settings saved!", parent=top)
             top.destroy()

        btn_save = tk.Button(top, text="Save & Close", command=save_settings)
        btn_save.pack(side="bottom", pady=10)

        # Logic for Key Capture
        self.capturing = False
        
        def start_capture():
            self.capturing = True
            btn_reset.config(text="Press any key...")
            top.focus_force()

        btn_reset.config(command=start_capture)

        def on_key(event):
            if not self.capturing: return
            self.capturing = False
            
            new_key = event.keysym
            if len(event.char) > 0 and ord(event.char) > 31:
                new_key = event.char
            
            cfg = load_config()
            cfg["reset_key"] = new_key
            save_config(cfg)
            self.config = cfg # Update local config
            self.input_handler.update_config()
            
            btn_reset.config(text=f"Current: {new_key}")
            
        top.bind("<Key>", on_key)

    def show_help(self):
        msg = (
            "Mouse Scroll Counter\n\n"
            "Top Green Number: Scroll Up Count\n"
            "Bottom Red Number: Scroll Down Count\n\n"
            f"Press '{self.input_handler.reset_key}' to reset counters.\n"
            "Use Tray Icon to Change Settings or Exit."
        )
        # Using root as parent might make it invisible if root is transparent? 
        # But messagebox is usually OS native. Let's try.
        messagebox.showinfo("Help", msg)

def start_overlay(cmd_queue, input_handler):
    root = tk.Tk()
    app = Overlay(root, cmd_queue, input_handler)
    root.mainloop()
