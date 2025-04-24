# KillSwitch - 2D Fighting Game 🎮⚔️  
A pixel-art arcade fighting game combining competitive local play and immersive story battles.

## ✨ Features
- 🎭 Typewriter-style cutscene system with animated dialogue
- 👥 2-player local mode with map voting
- 🧠 Smart AI that reacts to player's decisions
- 🛡️ Shield & shield-break mechanics for tactical depth
- 👹 Boss transformation and flying attack system
- 🎮 Fully animated 2D pixel characters
- 🗺️ Arena previews before each fight

## 🛠️ Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/killswitch
   cd killswitch
   ```

2. Install dependencies:
   ```bash
   pip install pygame
   ```

3. Run the game:
   ```bash
   python main.py
   ```

## 🕹️ Controls

| Player | Move      | Jump | Crouch | Punch | Shield | Shoot (Z - story boss only) |
|--------|-----------|------|--------|--------|--------|------------------------------|
| P1     | A / D     | W    | S      | Space  | E      | Z                            |
| P2     | ← / →     | ↑    | ↓      | RShift | —      | —                            |

## 📁 Project Structure

```
characters/       # All character sprites and portraits
map/              # Arena images and map buttons
assets/           # Backgrounds and UI
sounds/           # SFX like clicks and confirms
music/            # Background music
main.py           # Game launcher
menu.py           # Main and submenus
local.py          # Local match logic
story_mode.py     # Story mode handler
story_cutscene.py # Intro dialogue
demon_cutscene.py # Boss transition dialogue
story_wave1.py    # Wave 1 fight
story_wave2.py    # Boss fight (Demon Archon)
globals.py        # Contains all the global variables
collectibles.py   # Puts all the collectibles across the game
```

## 📋 Requirements

- Python 3.10+
- Pygame

## 🏁 Final Note

Thanks for playing **KillSwitch**. Can you survive Archon's final form?
