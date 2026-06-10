# Ashbourne

A top-down 2D RPG built in Python with Pygame. Dark fantasy, turn-based combat, and a story about institutional failure, buried decisions, and what gets left beneath a city.

---

## Story

The Order of Wardens sealed something beneath Ashbourne ten years ago. They chose silence over truth, and the city survived — for now.

You are a Warden. The cracks are returning. Three districts stand between you and the original source, and every answer you find makes the final choice harder.

---

## Features

- **4 districts** - The Warden's Post (hub), The Undercroft, The Merchant Quarter, and The Spire
- **Turn-based combat** with abilities, cooldowns, buffs, and enemy specials
- **6 enemy types** including bosses with unique mechanics (regeneration, summoning, ability mirroring)
- **Quest system** with multi-step quests and tracked progress
- **Dialogue system** with typewriter effect and branching choices
- **Inventory system** with usable items and story lore drops
- **Leveling system** with XP scaling per district
- **Moral choices** that affect how the story resolves
- **Camera system** with tile-based movement and collision

---

## Enemies

| Enemy | Special |
|---|---|
| Crawler | Moves first every turn |
| Pale One | High defense |
| Hollow Merchant | Steals gold on hit |
| Debt Collector | Heavy hitter |
| Echo | Copies your last ability |
| Remnant | Immune to physical damage |

| Boss | Special |
|---|---|
| The First Crack | Regenerates HP each turn |
| The Broker | Summons Debt Collectors |
| The Last Captain | Uses your own abilities against you |

---

## Abilities

Abilities unlock as you clear districts.

| Ability | Effect | Unlock |
|---|---|---|
| Counter | Halve incoming damage, strike back | Start |
| War Cry | +6 ATK for 3 turns | District 1 |
| Last Stand | Triple damage when HP < 30% | District 2 |
| Warden's Oath | Restore 25% max HP (single use) | District 3 |

---

## Controls

| Key | Action |
|---|---|
| W / A / S / D or Arrow keys | Move |
| E / Enter | Interact / Confirm |
| I | Open inventory |
| Escape | Back / Cancel |
| W / S (in menus) | Navigate |

---

## Installation

**Requirements:** Python 3.10+, Pygame 2.x

```bash
pip install pygame
```

**Run:**

```bash
cd Ashbourne/Game
python main.py
```

---

## Project Structure

```
Ashbourne/Game/
- main.py        - Game loop, state machine, rendering
- entities.py    - Player, enemies, NPCs, portals, interactables
- maps.py        - Tile maps, palettes, map data for all districts
- combat.py      - Turn-based combat manager
- dialogue.py    - Dialogue scripts and dialogue manager
- logic.py       - Damage, XP, leveling, items, abilities, buffs
- ui.py          - HUD, inventory screen, floating text, notifications
- data/
  - enemies.py   - Enemy and boss stats
  - items.py     - Item pool, story items, shop inventory
  - quests.py    - Quest definitions and quest manager
```

---

## Built as a learning project

This game was built step by step as an exercise in Python and Pygame — starting from a blank window and a moving rectangle, working up to a complete game loop with combat, dialogue, quests, and a camera system.
