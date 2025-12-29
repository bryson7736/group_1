# Random Dice Defense: Hell Chapter

A feature-rich Tower Defense game built with Python and Pygame, inspired by the mechanics of "Random Dice". Defend your base against waves of infernal enemies, unlock story chapters, and master the art of dice synergy!

## 🎮 Game Modes

### Story Mode: Hell Chapter
Embark on a journey through 5 challenging chapters, each with unique maps and increasing difficulty.
- **Chapter 1: Hell Gate**
- **Chapter 2: Burning Path**
- **Chapter 3: Demon Fortress**
- **Chapter 4: Chamber of Torment**
- **Chapter 5: Hell Lord's Throne**

*Note: You must complete the previous chapter to unlock the next one.*

### Practice Mode
Test your strategies in endless waves. How long can you survive?

## 🎲 Dice System

### Dice Types
- **Fire**: Deals splash damage.
- **Wind**: High attack speed.
- **Ice**: Slows enemies.
- **Poison**: Applies damage over time.
- **Iron**: High damage against bosses, can explode.
- **Multi**: Hits multiple targets.
- **Single**: High single-target damage (Sniper).
- **Broken**: A weak die that needs to be merged away.

### Mechanics
- **Spawning**: Spend SP (Mana) to spawn a random die. Cost increases with each spawn.
- **Merging**: Drag and drop a die onto another of the **same type** and **same dot count** to merge them into a random die of the next tier.
- **Synergies**: Place specific dice **adjacent** to each other (horizontally or vertically) to activate powerful field effects:
    - **Inferno** (Fire + Wind): Massive splash damage and speed.
    - **Toxic Spikes** (Iron + Poison): Iron applies poison, Poison deals more damage.
    - **Frost Volley** (Ice + Multi): Multi-shot slows enemies, Ice gains range.
    - **Sniper Nest** (Single + Wind): Massive range and damage boost.
    - **Magma** (Fire + Iron): Fire damage boost, Iron explodes on impact.
    - **Plague** (Poison + Multi): Poison spreads to nearby enemies.

## ⚔️ Enemies & Bosses

- **Standard Enemies**: Varying speed and HP.
- **Big Enemy**: Tougher variants that appear periodically.
- **True Boss**: The ultimate challenge appearing at the end of chapters.
    - **Phases**: Cycles between Attack, Defense, and Heal states.
    - **Mechanics**: Watch out for the Boss's target indicator! Merge the targeted die to "Flee" and dodge the attack.

## 🛠️ Progression & Upgrades

- **Lobby Upgrades**: Use Coins earned from battles to permanently upgrade your stats:
    - **Damage**: +10% Global Damage
    - **Speed**: +5% Global Attack Speed
    - **Crit**: +5% Critical Hit Rate
- **In-Game Upgrades**: Spend SP during a match to temporarily boost specific dice types.

## 💰 "Premium" Features (Parody)

This game features a satirical take on mobile game monetization:
- **Fake Ads**: Popups that interrupt gameplay (click 'X' to close).
- **Fake Payment Store**: A simulated payment screen to "buy" coins or "Remove Ads".
    - *Cheat*: Enter any 16-digit card number to "succeed".
- **Creator Button**: A hidden blue button in the bottom-left of the main menu. Click it to instantly unlock everything and get rich!

## 🚀 Installation & Running

1.  **Prerequisites**: Python 3.x installed.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Game**:
    ```bash
    python main.py
    ```

## ⌨️ Controls

- **Mouse Left Click**: Spawn dice / Select & Drag to merge.
- **Mouse Right Click**: Deselect / Cancel.
- **Space**: Spawn Die shortcut.
- **1-5**: Adjust Game Speed (Higher speeds may be locked behind "Premium").
- **N**: Call Next Wave early.
- **R**: Restart (during Game Over).
- **ESC**: Pause / Back to Lobby.

## 👥 Contributors

- **sutender**
- **Bryson**
- **Chiang-Ian**
- **洪崧祐**
- **peppa1122ee13**
