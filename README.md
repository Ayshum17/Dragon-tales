# Dragon Climb

A vertical climbing dodge game where you control a dragon climbing through a cave filled with obstacles. Avoid rock walls and fireballs while climbing as high as you can!

## How to Run

### From Python (Development Mode)

```bash
python main.py
```

Requirements:
- Python 3.10+
- Tkinter (included with standard Python on Windows)
- Pillow (for asset generation only)

### As a Standalone Windows Application

Double-click `dist/DragonClimb.exe` to play immediately without installing Python.

## Game Controls

| Control | Action |
|---------|--------|
| **TOP** button / Up Arrow / W | Move dragon up |
| **BOTTOM** button / Down Arrow / S | Move dragon down |
| **SPACE** | Boost upward |
| **P** | Pause / Resume |
| **M** | Toggle sound on/off |
| **R** | Restart (on Game Over screen) |
| **ESC** | Pause / Return to menu |
| **ENTER / SPACE** | Start game (on menu) |

## Game Features

- **Main Menu** - Start the game, view best score, see controls
- **Dragon Movement** - Move up/down with buttons or keyboard
- **Obstacles** - Random rock walls (top/bottom) and fireballs
- **Collision Detection** - Game ends when you hit an obstacle
- **Score System** - Points increase over time
- **Height Tracking** - Climb higher for more height
- **Best Score** - Saved persistently across sessions
- **Difficulty Progression** - Obstacles speed up and gaps shrink as you climb
- **Pause** - Pause and resume the game at any time
- **Game Over Screen** - View score, restart, or return to menu
- **Sound Effects** - Jump, crash, and score sounds (toggleable)

## How to Build the EXE

### Prerequisites

```bash
pip install pyinstaller
pip install pillow
```

### Clean Build (One-File)

```bash
pyinstaller --noconfirm --clean --onefile --windowed --name "DragonClimb" --add-data "assets;assets" --icon=assets/dragon_climb.ico main.py
```

### Clean Build (One-Directory)

```bash
pyinstaller --noconfirm --clean --windowed --name "DragonClimb" --add-data "assets;assets" --icon=assets/dragon_climb.ico main.py
```

The final executable is located at:
- **One-file:** `dist/DragonClimb.exe`
- **One-directory:** `dist/DragonClimb/DragonClimb.exe`

### Regenerating Assets

```bash
python generate_assets.py
```

## Project Structure

```
dragon_climb/
│
├── main.py              # Entry point
├── game.py              # Game logic (screens, dragon, obstacles, collision)
├── settings.py          # Constants, resource paths, save system
├── generate_assets.py   # Asset generation script (images, sounds, icon)
├── README.md            # This file
├── requirements.txt     # Python dependencies
│
├── assets/              # Game assets
│   ├── dragon_1.png     # Dragon frame 1
│   ├── dragon_2.png     # Dragon frame 2
│   ├── dragon.png       # Combined dragon sprite
│   ├── obstacle_top.png # Top rock wall
│   ├── obstacle_bottom.png # Bottom rock wall
│   ├── obstacle.png     # Fireball obstacle
│   ├── background.png   # Sky background
│   ├── dragon_climb.ico # Application icon
│   ├── dragon_climb_icon.png # Icon (PNG)
│   ├── sound_jump.wav   # Jump sound
│   ├── sound_crash.wav  # Crash sound
│   └── sound_score.wav  # Score sound
│
├── saves/               # Save data (development mode)
│   └── best_score.json  # Best score file
│
├── build/               # PyInstaller build artifacts
├── dist/                # Final executable output
│   └── DragonClimb.exe  # Standalone executable
└── DragonClimb.spec     # PyInstaller spec file
```

## PyInstaller Requirements

- **PyInstaller 6.0+** - For packaging the game into an EXE
- **Pillow 10.0+** - For generating game assets (not needed at runtime)
- Assets are bundled using `--add-data "assets;assets"` (Windows separator `;`)
- Save data is stored in `%APPDATA%/DragonClimb/` when running as EXE
- The `--windowed` flag ensures no console window appears
- The `--icon` flag sets the application icon

## Asset Path System

The game uses a robust path system that works in both development and packaged modes:

- `get_resource_path()` - Resolves asset paths using `sys._MEIPASS` when frozen
- `get_save_path()` - Returns a writable directory for save data
- Save data is stored outside the read-only PyInstaller bundle

## Testing

Run the automated test suite:

```bash
python test_game.py
```

This verifies:
- All assets exist and load correctly
- Save system works (read, write, corruption recovery)
- Game initialization and all screens
- Dragon movement (TOP/BOTTOM buttons)
- Obstacle spawning and collision
- Pause, game over, and restart
- Score, height, and difficulty systems