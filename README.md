# Mouse Scroll Counter

A transparent overlay that counts your mouse scroll wheel actions (Up/Down). Designed to be unobtrusive and work over games (Borderless Windowed recommended).

## Features

- **Overlay**: Minimalist green/red counters in the top-right corner.
- **Tray Icon**: Control the application, access settings, or exit.
- **Customizable**: Change the reset hotkey easily.
- **Click-Through**: The overlay is transparent to mouse clicks.

## Running from Source

1. **Install Python 3.x**
2. **Install Dependencies**:
   ```powershell
   pip install pynput pystray Pillow
   ```
3. **Run**:
   ```powershell
   python main.py
   ```

## Building Executable (EXE)

To create a standalone `.exe` file that doesn't require Python to be installed:

1. **Install PyInstaller**:
   ```powershell
   pip install pyinstaller
   ```
2. **Build**:
   ```powershell
   pyinstaller --noconsole --onefile --name="MouseScrollCounter" main.py
   ```
   - `--noconsole`: Hides the black command line window.
   - `--onefile`: Bundles everything into a single `.exe` file.

3. **Locate EXE**:
   The `MouseScrollCounter.exe` will be found in the `dist` folder.

## Configuration

The application creates a `config.json` file in the same directory as the executable/script to store your reset key preference.