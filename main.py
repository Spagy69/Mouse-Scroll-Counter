import threading
import tkinter as tk
import pystray
from PIL import Image, ImageDraw
import sys
import os
import queue

# Import from modified overlay
from overlay import start_overlay
from input_handler import InputHandler

def create_image():
    width = 64
    height = 64
    color = "green"
    image = Image.new('RGB', (width, height), color)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill="blue")
    dc.rectangle((0, height // 2, width // 2, height), fill="blue")
    return image

def run_tray(cmd_queue, stop_event):
    def on_settings(icon, item):
        cmd_queue.put("settings")
    
    def on_help(icon, item):
        cmd_queue.put("help")
        
    def on_exit(icon, item):
        cmd_queue.put("quit")
        icon.stop()
        stop_event.set()

    menu = pystray.Menu(
        pystray.MenuItem("Help", on_help),
        pystray.MenuItem("Change Reset Key", on_settings),
        pystray.MenuItem("Exit", on_exit)
    )
    
    icon = pystray.Icon("ScrollCounter", create_image(), "Scroll Counter", menu)
    icon.run()

if __name__ == "__main__":
    # Queue for communication between Tray (Thread) and Overlay (Main Thread/Tkinter)
    cmd_queue = queue.Queue()
    stop_event = threading.Event()

    # Input Handler
    # Pass dummy callback, we poll in overlay
    input_handler = InputHandler(lambda u, d: None)
    input_handler.start()

    # Start Tray in separate thread
    tray_thread = threading.Thread(target=run_tray, args=(cmd_queue, stop_event))
    tray_thread.start()

    # Start Overlay in MAIN Thread (Tkinter requirement)
    # This blocks until window is closed or quit
    try:
        start_overlay(cmd_queue, input_handler)
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        input_handler.stop()
        if not stop_event.is_set():
            # If overlay closed by other means, kill tray
            # We can't easily kill pystray from outside its thread if it doesn't expose a handle
            # But the daemon thread will die when main exits, except pystray might not be daemon.
            # We'll rely on os._exit possibly if it hangs.
            pass
        
    os._exit(0)
