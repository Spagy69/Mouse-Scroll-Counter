# Mouse Scroll Counter

A transparent, click-through overlay that counts your mouse scroll wheel actions. It sits unobtrusively on your screen and works seamlessly over games and other full-screen applications.

## Features

- **Double Counter**: 
  - **Green Number**: Tracks "Scroll Up" actions.
  - **Red Number**: Tracks "Scroll Down" actions.
- **Modern Overlay**: Transparent background with "Ubuntu Bold" font for high visibility.
- **Fully Customizable**:
  - **Scaling**: Resize the overlay from **100% to 500%** to fit your visual preference.
  - **Positioning**: Automatically snaps to the top-right corner, but can be fine-tuned with manual position controls.
  - **Multi-Monitor**: Select exactly which monitor displays the overlay.
- **System Tray Integration**: Minimized to the tray with a custom mouse icon.

## Quick Start

1. Go to the **Releases** section of this repository.
2. Download the latest `MouseScrollCounter.exe`.
3. Run the executable.
4. The overlay will appear, and a Mouse icon will be added to your system tray.

## How to Use

### The Overlay
- **Scroll Up**: Increases the top green number.
- **Scroll Down**: Increases the bottom red number.
- **Reset**: Press the configured Reset Key (Default: `r`) to zero out counts.

### Settings Menu
Right-click the **System Tray Icon** and select **Settings** to open the configuration window.

- **Monitor Selection**: Choose which display screen holds the overlay.
- **Scale**: Use the slider to adjust the size of the overlay (text and window) from 1x to 5x.
- **Position Adjustment**: Use the **Arrow Buttons** (▲ ▼ ◄ ►) to nudge the overlay pixel-by-pixel for perfect alignment.
- **Reset Key**: Click the button and press any key to define a new hotkey for resetting counters.
- **Save & Close**: Persists your changes to `config.json` and closes the window.

## Running from Source

**Requirements**: Python 3.12+

1. **Install Dependencies**:
   ```powershell
   pip install pynput pystray Pillow
   ```
2. **Run the Script**:
   ```powershell
   python main.py
   ```

## Building the Executable

If you want to modify the code and rebuild the standalone `.exe`:

1. **Install PyInstaller**:
   ```powershell
   pip install pyinstaller
   ```
2. **Build**:
   Run the following command in the project root:
   ```powershell
   python -m PyInstaller --noconsole --onefile --icon="icons/mouse.png" --add-data="icons;icons" --add-data="fonts;fonts" --name="MouseScrollCounter" main.py
   ```
3. Find your new executable in the `dist` folder.