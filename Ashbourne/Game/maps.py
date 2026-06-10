import pygame

# Tile constants
T_FLOOR = 0
T_WALL  = 1

TILE_SIZE = 32

# Palette per district
PALETTES = {
    "hub": {
        T_FLOOR: (70, 65, 60),
        T_WALL:  (100, 90, 80),
        "accent": (200, 140, 60),
        "bg":     (30, 27, 24),
    },
    "undercroft": {
        T_FLOOR: (45, 50, 65),
        T_WALL:  (60, 65, 85),
        "accent": (80, 100, 140),
        "bg":     (15, 18, 28),
    },
    "merchant": {
        T_FLOOR: (80, 65, 30),
        T_WALL:  (100, 80, 40),
        "accent": (200, 160, 50),
        "bg":     (30, 22, 10),
    },
    "spire": {
        T_FLOOR: (80, 80, 85),
        T_WALL:  (110, 110, 115),
        "accent": (180, 180, 190),
        "bg":     (35, 35, 40),
    },
    "crack": {
        T_FLOOR: (10, 10, 10),
        T_WALL:  (20, 20, 20),
        "accent": (60, 50, 80),
        "bg":     (0, 0, 0),
    },
}

# Map data definitions
# Each map: tiles (2D list), palette_key, entity_spawns, portals, interactables

def _parse(rows):
    """Convert list-of-strings map into 2D int array."""
    result = []
    for row in rows:
        result.append([int(c) for c in row.split()])
    return result

# ── HUB: The Warden's Post ────────────────────────────────────────────────────
HUB_TILES = _parse([
    "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 1 1 1 1 1 0 0 0 0 0 0 0 0 1 1 1 1 1 0 0 0 1",
    "1 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1",
    "1 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1",
    "1 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1",
    "1 0 0 1 0 1 1 1 0 0 0 0 0 0 0 0 1 0 1 1 1 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 1 1 0 1 1 1 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 1 1 1 1 1 0 1 1 1 1 1 0 1 1 1 1 0 1 1 1 1 1 1 1",
])

# ── UNDERCROFT FLOOR 1 ────────────────────────────────────────────────────────
UC1_TILES = _parse([
    "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 1 1 0 1 1 1 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 0 0 0 1",
    "1 1 1 0 1 1 0 0 0 0 0 0 0 0 0 1 0 1 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 1 1 0 1 1 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 1 1 1 0 0 0 0 0 0 0 0 0 1 1 0 1 1 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 1 1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1 1",
])

# ── UNDERCROFT FLOOR 2 ────────────────────────────────────────────────────────
UC2_TILES = _parse([
    "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 1 0 1 1 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1 1 1",
])

# ── UNDERCROFT BOSS ROOM ──────────────────────────────────────────────────────
# ── MERCHANT QUARTER FLOOR 1 ──────────────────────────────────────────────────
MQ1_TILES = _parse([
    "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 1 1 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 1",
    "1 0 0 1 1 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 1 1 0 1 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 1 1 1 1 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 1 1 0 1 1 0 0 0 0 0 0 1 1 0 1 1 0 0 1",
    "1 0 0 1 1 0 1 1 0 0 0 0 0 0 1 1 0 1 1 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1 1 1",
])

# ── MERCHANT QUARTER FLOOR 2 ──────────────────────────────────────────────────
MQ2_TILES = _parse([
    "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 1 1 1 0 1 1 1 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 1 1 1 1 1 1 1 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 1",
    "1 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1 1 1",
])

# ── MERCHANT QUARTER BOSS ROOM ────────────────────────────────────────────────
MQ_BOSS_TILES = _parse([
    "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1",
])

# ── SPIRE FLOOR 1 ─────────────────────────────────────────────────────────────
SP1_TILES = _parse([
    "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 1 1 1 1 0 0 0 0 0 1 1 1 1 0 0 0 0 1",
    "1 0 0 0 1 0 0 1 0 0 0 0 0 1 0 0 1 0 0 0 0 1",
    "1 0 0 0 1 0 0 1 0 0 0 0 0 1 0 0 1 0 0 0 0 1",
    "1 0 0 0 1 1 1 1 0 0 0 0 0 1 1 1 1 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1 1 1",
])

# ── SPIRE FLOOR 2 ─────────────────────────────────────────────────────────────
SP2_TILES = _parse([
    "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 1 1 1 1 1 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 1 1 1 1 1 1 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 1 1 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 1",
    "1 0 0 1 1 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1 1 1",
])

# ── SPIRE BOSS ROOM ───────────────────────────────────────────────────────────
SP_BOSS_TILES = _parse([
    "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1",
])

UC_BOSS_TILES = _parse([
    "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
    "1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1",
])


class MapData:
    def __init__(self, map_id, tiles, palette_key, player_start,
                 enemy_spawns=None, npc_spawns=None,
                 portals=None, interactables=None, music=None):
        self.map_id = map_id
        self.tiles = tiles
        self.height = len(tiles)
        self.width = len(tiles[0]) if tiles else 0
        self.palette_key = palette_key
        self.palette = PALETTES[palette_key]
        self.player_start = player_start      # (tile_x, tile_y)
        self.enemy_spawns = enemy_spawns or []
        self.npc_spawns = npc_spawns or []
        self.portals = portals or []
        self.interactables = interactables or []
        self.music = music

    def get_tile(self, tx, ty):
        if 0 <= ty < self.height and 0 <= tx < self.width:
            return self.tiles[ty][tx]
        return T_WALL

    def is_wall(self, tx, ty):
        return self.get_tile(tx, ty) == T_WALL

    def pixel_width(self):
        return self.width * TILE_SIZE

    def pixel_height(self):
        return self.height * TILE_SIZE


def build_maps():
    maps = {}

    # ── HUB ──────────────────────────────────────────────────────────────────
    maps["hub"] = MapData(
        map_id="hub",
        tiles=HUB_TILES,
        palette_key="hub",
        player_start=(12, 18),
        npc_spawns=[
            {"name": "Maren", "tx": 11, "ty": 5, "dialogue_key": "maren"},
        ],
        portals=[
            # Bottom gap at col 12 → Undercroft F1
            {"tx": 12, "ty": 19, "target": "undercroft_1", "ttx": 11, "tty": 1,
             "requires": None, "label": "The Undercroft"},
            # Left side → Merchant Quarter
            {"tx": 1, "ty": 5, "target": "merchant_1", "ttx": 11, "tty": 1,
             "requires": "district_1_done", "label": "Merchant Quarter"},
            # Right side → The Spire
            {"tx": 23, "ty": 5, "target": "spire_1", "ttx": 11, "tty": 1,
             "requires": "district_2_done", "label": "The Spire"},
            # Top center → The Crack
            {"tx": 12, "ty": 1, "target": "crack", "ttx": 9, "tty": 11,
             "requires": "district_3_done", "label": "The Crack"},
        ],
        interactables=[
            {"tx": 11, "ty": 9,  "type": "notice_board", "data": {}},
            {"tx": 22, "ty": 12, "type": "chest",
             "data": {"item": {"name": "Health Potion", "type": "heal",
                               "value": 35, "price": 0}, "opened": False}},
        ],
    )

    # ── UNDERCROFT FLOOR 1 ────────────────────────────────────────────────────
    maps["undercroft_1"] = MapData(
        map_id="undercroft_1",
        tiles=UC1_TILES,
        palette_key="undercroft",
        player_start=(11, 1),
        enemy_spawns=[
            {"type": "Crawler",  "tx": 5,  "ty": 4},
            {"type": "Crawler",  "tx": 14, "ty": 7},
            {"type": "Crawler",  "tx": 8,  "ty": 12},
            {"type": "Crawler",  "tx": 2,  "ty": 17},
            {"type": "Crawler",  "tx": 19, "ty": 17},
            {"type": "Pale One", "tx": 3,  "ty": 10},
            {"type": "Pale One", "tx": 18, "ty": 14},
            {"type": "Pale One", "tx": 12, "ty": 16},
        ],
        portals=[
            # Return to hub
            {"tx": 11, "ty": 19, "target": "hub", "ttx": 12, "tty": 18,
             "requires": None, "label": "Warden's Post"},
            # Down to floor 2
            {"tx": 11, "ty": 1,  "target": "undercroft_2", "ttx": 10, "tty": 18,
             "requires": None, "label": "Deeper..."},
        ],
        interactables=[
            {"tx": 7, "ty": 5, "type": "tunnel",
             "data": {"quest": "what_was_sealed", "step": "find_tunnel",
                      "text": [
                          "A section of the tunnel has collapsed.",
                          "Order markings are carved into the exposed stone.",
                          "Someone sealed this passage intentionally.",
                          "Quest updated: What Was Sealed."
                      ]}},
            {"tx": 15, "ty": 5, "type": "chest",
             "data": {"item": {"name": "Health Potion", "type": "heal",
                               "value": 35, "price": 0}, "opened": False}},
            {"tx": 3, "ty": 13, "type": "chest",
             "data": {"item": {"name": "Health Potion", "type": "heal",
                               "value": 35, "price": 0}, "opened": False}},
        ],
    )

    # ── UNDERCROFT FLOOR 2 ────────────────────────────────────────────────────
    maps["undercroft_2"] = MapData(
        map_id="undercroft_2",
        tiles=UC2_TILES,
        palette_key="undercroft",
        player_start=(10, 18),
        enemy_spawns=[
            {"type": "Crawler",  "tx": 4,  "ty": 4},
            {"type": "Crawler",  "tx": 15, "ty": 12},
            {"type": "Crawler",  "tx": 2,  "ty": 8},
            {"type": "Crawler",  "tx": 19, "ty": 3},
            {"type": "Pale One", "tx": 8,  "ty": 8},
            {"type": "Pale One", "tx": 17, "ty": 5},
            {"type": "Pale One", "tx": 5,  "ty": 15},
            {"type": "Pale One", "tx": 18, "ty": 17},
        ],
        portals=[
            {"tx": 10, "ty": 19, "target": "undercroft_1", "ttx": 11, "tty": 18,
             "requires": None, "label": "Up"},
            {"tx": 10, "ty": 1,  "target": "undercroft_boss", "ttx": 9, "tty": 11,
             "requires": None, "label": "Boss Chamber"},
        ],
        interactables=[
            {"tx": 13, "ty": 9, "type": "dead_warden",
             "data": {"quest": "what_was_sealed", "step": "recover_logbook",
                      "gives_item": {"name": "Warden's Logbook", "type": "lore",
                                     "value": 0, "price": 0,
                                     "desc": "A dead warden's logbook. The final entry cuts off mid-sentence."},
                      "text": [
                          "A Warden's body, propped against the wall.",
                          "Dead for years. Maybe ten.",
                          "In the coat pocket: a sealed logbook.",
                          "You take it.",
                          "Quest updated: What Was Sealed."
                      ]}},
            {"tx": 5, "ty": 5, "type": "chest",
             "data": {"item": {"name": "Large HP Potion", "type": "heal",
                               "value": 70, "price": 0}, "opened": False}},
            {"tx": 18, "ty": 14, "type": "chest",
             "data": {"item": {"name": "Health Potion", "type": "heal",
                               "value": 35, "price": 0}, "opened": False}},
        ],
    )

    # ── UNDERCROFT BOSS ROOM ──────────────────────────────────────────────────
    maps["undercroft_boss"] = MapData(
        map_id="undercroft_boss",
        tiles=UC_BOSS_TILES,
        palette_key="undercroft",
        player_start=(9, 11),
        enemy_spawns=[
            {"type": "The First Crack", "tx": 9, "ty": 3, "is_boss": True},
        ],
        portals=[
            {"tx": 9, "ty": 12, "target": "undercroft_2", "ttx": 10, "tty": 2,
             "requires": None, "label": "Back"},
        ],
        interactables=[],
    )

    # ── MERCHANT QUARTER FLOOR 1 ─────────────────────────────────────────────────────
    maps["merchant_1"] = MapData(
        map_id="merchant_1",
        tiles=MQ1_TILES,
        palette_key="merchant",
        player_start=(11, 1),
        enemy_spawns=[
            {"type": "Hollow Merchant", "tx": 5,  "ty": 4},
            {"type": "Hollow Merchant", "tx": 14, "ty": 7},
            {"type": "Hollow Merchant", "tx": 8,  "ty": 12},
            {"type": "Debt Collector",  "tx": 3,  "ty": 10},
            {"type": "Debt Collector",  "tx": 18, "ty": 14},
            {"type": "Debt Collector",  "tx": 12, "ty": 16},
            {"type": "Hollow Merchant", "tx": 2,  "ty": 17},
            {"type": "Hollow Merchant", "tx": 19, "ty": 17},
        ],
        portals=[
            {"tx": 11, "ty": 19, "target": "hub", "ttx": 12, "tty": 18,
             "requires": None, "label": "Warden's Post"},
            {"tx": 11, "ty": 1,  "target": "merchant_2", "ttx": 10, "tty": 18,
             "requires": None, "label": "Deeper..."},
        ],
        interactables=[
            {"tx": 7, "ty": 5, "type": "hidden_office",
             "data": {"quest": "the_orders_debt", "step": "find_records",
                      "text": [
                          "A hidden office behind a false wall.",
                          "The Order's financial records are here.",
                          "Payments from The Broker. Regular. Large.",
                          "Quest updated: The Order's Debt."
                      ]}},
            {"tx": 15, "ty": 5, "type": "chest",
             "data": {"item": {"name": "Health Potion", "type": "heal",
                               "value": 35, "price": 0}, "opened": False}},
            {"tx": 3, "ty": 13, "type": "chest",
             "data": {"item": {"name": "Mana Potion", "type": "mana",
                               "value": 30, "price": 0}, "opened": False}},
        ],
    )

    # ── MERCHANT QUARTER FLOOR 2 ────────────────────────────────────────────────────
    maps["merchant_2"] = MapData(
        map_id="merchant_2",
        tiles=MQ2_TILES,
        palette_key="merchant",
        player_start=(10, 18),
        enemy_spawns=[
            {"type": "Hollow Merchant", "tx": 4,  "ty": 4},
            {"type": "Hollow Merchant", "tx": 15, "ty": 12},
            {"type": "Debt Collector",  "tx": 2,  "ty": 8},
            {"type": "Debt Collector",  "tx": 19, "ty": 3},
            {"type": "Debt Collector",  "tx": 8,  "ty": 8},
            {"type": "Hollow Merchant", "tx": 17, "ty": 5},
            {"type": "Debt Collector",  "tx": 5,  "ty": 15},
            {"type": "Hollow Merchant", "tx": 18, "ty": 17},
        ],
        portals=[
            {"tx": 10, "ty": 19, "target": "merchant_1", "ttx": 11, "tty": 18,
             "requires": None, "label": "Up"},
            {"tx": 10, "ty": 1,  "target": "merchant_boss", "ttx": 9, "tty": 11,
             "requires": None, "label": "Boss Chamber"},
        ],
        interactables=[
            {"tx": 13, "ty": 9, "type": "broker_contact",
             "data": {"quest": "the_orders_debt", "step": "find_contact",
                      "text": [
                          "The Broker's contact.",
                          "He knows you know.",
                          "He offers a deal.",
                          "Quest updated: The Order's Debt."
                      ]}},
            {"tx": 5, "ty": 5, "type": "chest",
             "data": {"item": {"name": "Large HP Potion", "type": "heal",
                               "value": 70, "price": 0}, "opened": False}},
            {"tx": 18, "ty": 14, "type": "chest",
             "data": {"item": {"name": "Health Potion", "type": "heal",
                               "value": 35, "price": 0}, "opened": False}},
        ],
    )

    # ── MERCHANT QUARTER BOSS ROOM ────────────────────────────────────────────────
    maps["merchant_boss"] = MapData(
        map_id="merchant_boss",
        tiles=MQ_BOSS_TILES,
        palette_key="merchant",
        player_start=(9, 11),
        enemy_spawns=[
            {"type": "The Broker", "tx": 9, "ty": 3, "is_boss": True},
        ],
        portals=[
            {"tx": 9, "ty": 12, "target": "merchant_2", "ttx": 10, "tty": 2,
             "requires": None, "label": "Back"},
        ],
        interactables=[],
    )

    # ── SPIRE FLOOR 1 ─────────────────────────────────────────────────────────
    maps["spire_1"] = MapData(
        map_id="spire_1",
        tiles=SP1_TILES,
        palette_key="spire",
        player_start=(11, 1),
        enemy_spawns=[
            {"type": "Echo",     "tx": 5,  "ty": 4},
            {"type": "Echo",     "tx": 14, "ty": 7},
            {"type": "Remnant",  "tx": 8,  "ty": 12},
            {"type": "Echo",     "tx": 3,  "ty": 10},
            {"type": "Remnant",  "tx": 18, "ty": 14},
            {"type": "Echo",     "tx": 12, "ty": 16},
            {"type": "Remnant",  "tx": 2,  "ty": 17},
            {"type": "Echo",     "tx": 19, "ty": 17},
        ],
        portals=[
            {"tx": 11, "ty": 19, "target": "hub", "ttx": 12, "tty": 18,
             "requires": None, "label": "Warden's Post"},
            {"tx": 11, "ty": 1,  "target": "spire_2", "ttx": 10, "tty": 18,
             "requires": None, "label": "Deeper..."},
        ],
        interactables=[
            {"tx": 7, "ty": 5, "type": "journal_1",
             "data": {"quest": "the_last_order", "step": "journal_1",
                      "gives_item": {"name": "Captain's Journal I", "type": "lore",
                                     "value": 0, "price": 0,
                                     "desc": "The Captain knew the cracks would return early."},
                      "text": [
                          "Journal 1:",
                          "\"The order knew the cracks would return early.\"",
                          "The Captain wrote it himself.",
                          "Quest updated: The Last Order."
                      ]}},
            {"tx": 15, "ty": 5, "type": "chest",
             "data": {"item": {"name": "Health Potion", "type": "heal",
                               "value": 35, "price": 0}, "opened": False}},
            {"tx": 3, "ty": 13, "type": "chest",
             "data": {"item": {"name": "Mana Potion", "type": "mana",
                               "value": 30, "price": 0}, "opened": False}},
        ],
    )

    # ── SPIRE FLOOR 2 ────────────────────────────────────────────────────────
    maps["spire_2"] = MapData(
        map_id="spire_2",
        tiles=SP2_TILES,
        palette_key="spire",
        player_start=(10, 18),
        enemy_spawns=[
            {"type": "Echo",     "tx": 4,  "ty": 4},
            {"type": "Remnant",  "tx": 15, "ty": 12},
            {"type": "Echo",     "tx": 2,  "ty": 8},
            {"type": "Remnant",  "tx": 19, "ty": 3},
            {"type": "Echo",     "tx": 8,  "ty": 8},
            {"type": "Remnant",  "tx": 17, "ty": 5},
            {"type": "Echo",     "tx": 5,  "ty": 15},
            {"type": "Remnant",  "tx": 18, "ty": 17},
        ],
        portals=[
            {"tx": 10, "ty": 19, "target": "spire_1", "ttx": 11, "tty": 18,
             "requires": None, "label": "Up"},
            {"tx": 10, "ty": 1,  "target": "spire_boss", "ttx": 9, "tty": 11,
             "requires": None, "label": "Boss Chamber"},
        ],
        interactables=[
            {"tx": 13, "ty": 9, "type": "journal_2",
             "data": {"quest": "the_last_order", "step": "journal_2",
                      "gives_item": {"name": "Captain's Journal II", "type": "lore",
                                     "value": 0, "price": 0,
                                     "desc": "The Order voted on whether to warn the city."},
                      "text": [
                          "Journal 2:",
                          "\"The Order voted on whether to warn the city or handle it quietly.\"",
                          "The Captain voted for silence.",
                          "Quest updated: The Last Order."
                      ]}},
            {"tx": 5, "ty": 5, "type": "journal_3",
             "data": {"quest": "the_last_order", "step": "journal_3",
                      "gives_item": {"name": "Captain's Journal III", "type": "lore",
                                     "value": 0, "price": 0,
                                     "desc": "They chose silence. The Captain sealed himself in as penance."},
                      "text": [
                          "Journal 3:",
                          "\"They chose silence. The Captain sealed himself in as penance.\"",
                          "The last words.",
                          "Quest updated: The Last Order."
                      ]}},
            {"tx": 18, "ty": 14, "type": "chest",
             "data": {"item": {"name": "Mana Potion", "type": "mana",
                               "value": 30, "price": 0}, "opened": False}},
            {"tx": 5, "ty": 15, "type": "chest",
             "data": {"item": {"name": "Mana Potion", "type": "mana",
                               "value": 30, "price": 0}, "opened": False}},
        ],
    )

    # ── SPIRE BOSS ROOM ───────────────────────────────────────────────────────────
    maps["spire_boss"] = MapData(
        map_id="spire_boss",
        tiles=SP_BOSS_TILES,
        palette_key="spire",
        player_start=(9, 11),
        enemy_spawns=[
            {"type": "The Last Captain", "tx": 9, "ty": 3, "is_boss": True},
        ],
        portals=[
            {"tx": 9, "ty": 12, "target": "spire_2", "ttx": 10, "tty": 2,
             "requires": None, "label": "Back"},
        ],
        interactables=[],
    )

    # ── THE CRACK ─────────────────────────────────────────────────────────────
    maps["crack"] = MapData(
        map_id="crack",
        tiles=_parse([
            "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
            "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
            "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
            "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
            "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
            "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
            "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
            "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
            "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
            "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
            "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
            "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1",
            "1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1",
        ]),
        palette_key="crack",
        player_start=(9, 11),
        enemy_spawns=[],
        npc_spawns=[
            {"name": "Broker", "tx": 5, "ty": 5, "dialogue_key": "crack_broker"},
            {"name": "First Crack", "tx": 9, "ty": 3, "dialogue_key": "crack_first"},
            {"name": "Captain", "tx": 13, "ty": 5, "dialogue_key": "crack_captain"},
        ],
        portals=[
            {"tx": 9, "ty": 12, "target": "hub", "ttx": 12, "tty": 18,
             "requires": None, "label": "Back"},
        ],
        interactables=[
            {"tx": 9, "ty": 2, "type": "final_choice",
             "data": {"text": ["The Crack. The original one.",
                               "The same choice. The same math.",
                               "Seal it, or destroy it."]}},
        ],
    )

    return maps


ALL_MAPS = build_maps()
