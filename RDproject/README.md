# Random Dice Tower Defense (RDproject)

這是一個基於 Python 與 Pygame 開發的塔防遊戲，靈感來自於手遊《隨機骰子 (Random Dice)》。

## 遊戲描述

在遊戲中，玩家需要透過召喚與合併骰子來抵禦一波又一波的敵人。
- **召喚骰子**：消耗金幣在棋盤上生成一顆隨機骰子。
- **合併骰子**：將一顆骰子拖曳到另一顆同類型且同等級的骰子上進行合併，升級為更高一級的骰子（類型將隨機變換）。
- **骰子類型**：
    - **Single (單體)**：基礎輸出，射程遠且單發傷害穩定。
    - **Multi (多重)**：可同時攻擊多個目標。
    - **Freeze (冰凍)**：減緩敵人移動速度。
    - **Wind (風色)**：極快攻擊頻率。
    - **Poison (中毒)**：持續傷害效果。
    - **Iron (鋼鐵)**：對 Boss 造成額外傷害。
    - **Fire (火焰)**：群體濺射傷害。

## 運行需求

- Python 3.x
- Pygame

## 安裝步驟

1. 複製儲存庫或下載源代碼。
2. 安裝必要的依賴套件：

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
