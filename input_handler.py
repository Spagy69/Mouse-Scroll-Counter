from pynput import mouse, keyboard
import threading
from config import load_config

class InputHandler:
    def __init__(self, on_update_callback):
        self.up_count = 0
        self.down_count = 0
        self.on_update = on_update_callback
        
        self.config = load_config()
        self.reset_key = self.config.get("reset_key", "r")
        
        self.mouse_listener = None
        self.keyboard_listener = None
        self.running = False

    def start(self):
        self.running = True
        self.mouse_listener = mouse.Listener(on_scroll=self.on_scroll)
        self.keyboard_listener = keyboard.Listener(on_release=self.on_release)
        
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop(self):
        self.running = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def on_scroll(self, x, y, dx, dy):
        if dy > 0:
            self.up_count += 1
        elif dy < 0:
            self.down_count += 1
        
        # Trigger any immediate callback if needed, 
        # but the GUI polls the state usually.
        # self.on_update(self.up_count, self.down_count)

    def on_release(self, key):
        try:
            # Check char first
            if hasattr(key, 'char') and key.char == self.reset_key:
                self.reset_counts()
                return
            
            # Check keysym/name (e.g., 'f1', 'esc')
            # pynput key names usually don't match tkinter keysyms 1:1, but we do best effort
            if hasattr(key, 'name') and key.name == self.reset_key:
                self.reset_counts()
                return
                
            # Fallback for some keys where tkinter stores 'Return' but pynput has Key.enter
            # This handles the basic char cases mostly.
        except AttributeError:
            pass

    def reset_counts(self):
        self.up_count = 0
        self.down_count = 0

    def get_counts(self):
        return self.up_count, self.down_count

    def update_config(self):
        self.config = load_config()
        self.reset_key = self.config.get("reset_key", "r")
