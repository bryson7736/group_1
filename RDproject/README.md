# Random Dice Tower Defense (RDproject)

A Python-based Tower Defense game using Pygame, inspired by the mobile game "Random Dice".

## Description

In this game, you place and merge dice to defend your base against waves of enemies.
- **Spawn Dice**: Spend money to spawn a random die on the board.
- **Merge Dice**: Drag and drop a die onto another of the same type and level to merge them into a higher-level die (random type).
- **Types of Dice**:
    - **Single**: Basic damage dealer.
    - **Multi**: Hits multiple targets.
    - **Freeze**: Slows down enemies.

## Requirements

- Python 3.x
- Pygame

## Installation

1.  Clone the repository or download the source code.
2.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## How to Run

Navigate to the `RDproject` directory and run the `main.py` script:

```bash
cd RDproject
python main.py
```

## Controls

- **Left Click (Empty Slot)**: Spawn a new die (Cost increases).
- **Left Click (Die)**: Select a die. Click another compatible die to merge.
- **Right Click**: Cancel selection / Exit Trash mode.
- **1-5**: Change game speed.
- **T**: Cycle target mode (Nearest, Front, Weak, Strong).
- **N**: Start next wave immediately (if no enemies).
- **R**: Restart game (in Game Over screen).
- **ESC**: Return to Lobby / Cancel.

## Features

- **Wave System**: Infinite waves with increasing difficulty.
- **Boss Waves**: Every 5th wave is a boss wave with special abilities.
- **Upgrades**: Upgrade dice stats (Damage, Fire Rate, Cost) in the Lobby.
- **Loadout**: Choose your deck of dice (currently 3 types available).
