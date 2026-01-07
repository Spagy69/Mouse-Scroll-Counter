import tkinter as tk
from tkinter import messagebox
import ctypes
import platform
import queue
from config import load_config, save_config

class Overlay:
    def __init__(self, root, command_queue, input_handler):
        self.root = root
        self.command_queue = command_queue
        self.input_handler = input_handler
        self.root.title("Mouse Scroll Counter Overlay")
        
        # Window constraints
        self.root.overrideredirect(True)  # Remove title bar
        self.root.geometry("200x150")
        
        # Position top-right
        screen_width = self.root.winfo_screenwidth()
        x_pos = screen_width - 220
        y_pos = 20
        self.root.geometry(f"200x150+{x_pos}+{y_pos}")
        
        # Always on top
        self.root.attributes("-topmost", True)
        
        # Transparency
        bg_color = "#000001" 
        self.root.config(bg=bg_color)
        if platform.system() == "Windows":
            self.root.attributes("-transparentcolor", bg_color)

        # Labels
        self.font_style = ("Segoe UI", 24, "bold")
        
        # Green (Up)
        self.up_label = tk.Label(self.root, text="0", fg="#00ff00", bg=bg_color, font=self.font_style)
        self.up_label.pack(side="top", pady=10)
        
        # Red (Down)
        self.down_label = tk.Label(self.root, text="0", fg="#ff0000", bg=bg_color, font=self.font_style)
        self.down_label.pack(side="bottom", pady=10)

        # Click-through (Windows only)
        self.make_click_through()
        
        # Start Polling
        self.poll()

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
        top.title("Set Reset Key")
        top.geometry("300x150")
        
        # Ensure it's not transparent and has decorations
        top.attributes("-alpha", 1.0)
        top.attributes("-topmost", True)
        
        # Center checking
        ws = top.winfo_screenwidth()
        hs = top.winfo_screenheight()
        x = (ws/2) - (150)
        y = (hs/2) - (75)
        top.geometry(f"300x150+{int(x)}+{int(y)}")

        label = tk.Label(top, text="Press any key to set as Reset Key...", font=("Segoe UI", 12))
        label.pack(expand=True)
        
        # Variables to capture state to avoid multiple triggers
        self.capturing = True

        def on_key(event):
            if not self.capturing: return
            self.capturing = False
            
            new_key = event.keysym
            if len(event.char) > 0 and ord(event.char) > 31:
                new_key = event.char
            
            cfg = load_config()
            cfg["reset_key"] = new_key
            save_config(cfg)
            self.input_handler.update_config()
            
            messagebox.showinfo("Success", f"Reset key changed to: {new_key}", parent=top)
            top.destroy()
            
        top.bind("<Key>", on_key)
        top.focus_force() # Vital for catching key

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
