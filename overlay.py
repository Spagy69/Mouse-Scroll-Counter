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
        # Position logic
        # Defer position update until labels are created so we can update font size too
        pass
        
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
        
        
        # Initial Transform application (Position + Scale + Font)
        self.apply_transform()

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

    def apply_transform(self):
        monitors = get_monitors()
        monitor_index = self.config.get("monitor_index", 0)
        scale = self.config.get("scale", 1.0)
        offset_x = self.config.get("offset_x", 0)
        offset_y = self.config.get("offset_y", 0)
        
        # Base dimensions
        base_w = 200
        base_h = 150
        base_font_size = 24
        
        # Scaled dimensions
        w = int(base_w * scale)
        h = int(base_h * scale)
        font_size = int(base_font_size * scale)
        
        # Update Font
        font_name = self.config.get("font_name", "Segoe UI")
        new_font = (font_name, font_size, "bold")
        self.up_label.config(font=new_font)
        self.down_label.config(font=new_font)
        
        # Calculate Position
        if 0 <= monitor_index < len(monitors):
            m = monitors[monitor_index]
            # Calculate 5% margin
            margin_right = int(m["width"] * 0.05)
            margin_top = int(m["height"] * 0.05)
            
            # Position top-right with margin + offsets
            x_pos = m["right"] - w - margin_right + offset_x
            y_pos = m["top"] + margin_top + offset_y
        else:
            # Fallback
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            margin_right = int(screen_width * 0.05)
            margin_top = int(screen_height * 0.05)
            
            x_pos = screen_width - w - margin_right + offset_x
            y_pos = margin_top + offset_y
            
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

        # Force Topmost (Aggressive)
        if platform.system() == "Windows":
            try:
                # HWND_TOPMOST = -1
                # SWP_NOSIZE = 0x0001
                # SWP_NOMOVE = 0x0002
                # SWP_NOACTIVATE = 0x0010
                # SWP_SHOWWINDOW = 0x0040
                hwnd = self.root.winfo_id()
                ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010 | 0x0040)
            except Exception:
                pass
        
        # Standard fallback
        self.root.lift()
        self.root.attributes("-topmost", True)
        
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

        # Window Icon
        try:
            icon_path = get_resource_path(os.path.join("icons", "mouse.png"))
            if os.path.exists(icon_path):
                # Set icon for the title bar
                top.iconphoto(False, tk.PhotoImage(file=icon_path))
        except Exception:
            pass

        # === Monitor Selection ===
        lbl_monitor = tk.Label(top, text="Monitor:")
        lbl_monitor.pack(pady=(5, 0))
        
        monitors = get_monitors()
        monitor_options = [f"Monitor {i}" for i in range(len(monitors))]
        if not monitor_options:
            monitor_options = ["Monitor 0"]
        current_monitor = self.config.get("monitor_index", 0)
        if current_monitor >= len(monitor_options):
            current_monitor = 0
        combo_monitor = ttk.Combobox(top, values=monitor_options, state="readonly")
        combo_monitor.current(current_monitor)
        combo_monitor.pack(pady=2)

        def on_monitor_change(event):
            self.config["monitor_index"] = combo_monitor.current()
            self.apply_transform()
        combo_monitor.bind("<<ComboboxSelected>>", on_monitor_change)

        # === Scale Slider ===
        lbl_scale = tk.Label(top, text="Scale (100% - 500%):")
        lbl_scale.pack(pady=(10, 0))
        
        current_scale_val = int(self.config.get("scale", 1.0) * 100)
        scale_var = tk.IntVar(value=current_scale_val)
        
        def on_scale_change(val):
            new_scale = float(val) / 100.0
            self.config["scale"] = new_scale
            self.apply_transform()
            
        scl = tk.Scale(top, from_=100, to=500, orient=tk.HORIZONTAL, variable=scale_var, command=on_scale_change)
        scl.pack(fill="x", padx=20)

        # === Position Adjustment ===
        lbl_pos = tk.Label(top, text="Position Adjustment:")
        lbl_pos.pack(pady=(10, 2))
        
        pos_frame = tk.Frame(top)
        pos_frame.pack()
        
        def move(dx, dy):
            self.config["offset_x"] = self.config.get("offset_x", 0) + dx
            self.config["offset_y"] = self.config.get("offset_y", 0) + dy
            # Invert dy? No, screen coords: +y is down.
            self.apply_transform()

        btn_up = tk.Button(pos_frame, text="▲", width=3, command=lambda: move(0, -10))
        btn_up.grid(row=0, column=1)
        
        btn_left = tk.Button(pos_frame, text="◄", width=3, command=lambda: move(-10, 0))
        btn_left.grid(row=1, column=0)
        
        btn_down = tk.Button(pos_frame, text="▼", width=3, command=lambda: move(0, 10))
        btn_down.grid(row=1, column=1)
        
        btn_right = tk.Button(pos_frame, text="►", width=3, command=lambda: move(10, 0))
        btn_right.grid(row=1, column=2)

        # === Reset Key ===
        lbl_reset = tk.Label(top, text="Reset Key:")
        lbl_reset.pack(pady=(10, 0))
        
        btn_reset = tk.Button(top, text=f"Key: {self.input_handler.reset_key}")
        btn_reset.pack(pady=2)

        # === Save Button ===
        def save_settings():
             # Settings are already updated in self.config by live controls
             # Just need to write to disk
             save_config(self.config)
             messagebox.showinfo("Saved", "Settings saved!", parent=top)
             top.destroy()
        
        btn_save = tk.Button(top, text="Save & Close", command=save_settings, bg="#dddddd")
        btn_save.pack(side="bottom", pady=10, fill="x", padx=10)

        # Resize window to fit new content
        top.geometry("300x450")

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
            
            self.config["reset_key"] = new_key
            self.input_handler.reset_key = new_key 
            
            btn_reset.config(text=f"Key: {new_key}")
            
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
