# Mouse Scroll Counter

A transparent, click-through overlay that counts your mouse scroll wheel actions. It sits unobtrusively on your screen (customizable position) and works over games and other applications.

## Features

- **Vertical Counters**: Green number for "Scroll Up" and Red number for "Scroll Down", separated by a clean line.
- **Custom Font**: Uses "Ubuntu Bold" for a modern look (font included).
- **Multi-Monitor Support**: Choose which monitor the overlay appears on via Settings.
- **Auto-Positioning**: Automatically sits at the top-right corner (with 5% margin) of the selected monitor.
- **Tray Icon**: Minimalist mouse icon in the system tray to access Settings or Exit.
- **Settings**: Easily change the Reset Key or active Monitor.

## Installation / Running

### Method 1: Standalone Version (Recommended)
1. Go to the `dist` folder.
2. Run `MouseScrollCounter.exe`.
3. The application will launch in the system tray.

### Method 2: Running from Source
1. **Install Python 3.13+**
2. **Install Dependencies**:
   ```powershell
   pip install pynput pystray Pillow
   ```
3. **Run**:
   ```powershell
   python main.py
   ```

## Configuration

Right-click the **Tray Icon** (Mouse icon) and select **Settings**.
- **Reset Key**: Press any key to set it as the new reset hotkey (Default: `r`).
- **Monitor Index**: Select which display the overlay should appear on.

## Building from Source

To create a standalone `.exe` yourself:

1. Install PyInstaller:
   ```powershell
   pip install pyinstaller
   ```
2. Run the build command (ensure you are in the project root):
   ```powershell
   pyinstaller --noconsole --onefile --icon="icons/mouse.png" --add-data="icons;icons" --add-data="fonts;fonts" --name="MouseScrollCounter" main.py
   ```
   > Note: `--add-data` syntax depends on OS. For Windows, use `;`. For Linux/Mac, use `:`.

3. The new executable will be in the `dist` folder.