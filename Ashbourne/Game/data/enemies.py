import random

ENEMIES = {
    "Crawler": {
        "name": "Crawler",
        "hp": 35, "max_hp": 35,
        "atk": 10, "defense": 2,
        "gold": 6, "xp": 20,
        "color": (120, 180, 120),
        "special": "first",
        "desc": "Fast, skittering thing. Hits before you do.",
        "district": 1,
    },
    "Pale One": {
        "name": "Pale One",
        "hp": 70, "max_hp": 70,
        "atk": 12, "defense": 14,
        "gold": 12, "xp": 35,
        "color": (180, 180, 200),
        "special": None,
        "desc": "Slow and armored. Chip away at it.",
        "district": 1,
    },
    "Hollow Merchant": {
        "name": "Hollow Merchant",
        "hp": 50, "max_hp": 50,
        "atk": 16, "defense": 4,
        "gold": 15, "xp": 30,
        "color": (180, 140, 60),
        "special": "steal",
        "desc": "Was human. Still wearing the coat. Steals 10 gold on hit.",
        "district": 2,
    },
    "Debt Collector": {
        "name": "Debt Collector",
        "hp": 90, "max_hp": 90,
        "atk": 20, "defense": 10,
        "gold": 20, "xp": 50,
        "color": (140, 100, 40),
        "special": None,
        "desc": "Heavy armor, heavier fists.",
        "district": 2,
    },
    "Echo": {
        "name": "Echo",
        "hp": 150, "max_hp": 150,
        "atk": 16, "defense": 10,
        "gold": 25, "xp": 60,
        "color": (200, 200, 220),
        "special": "mirror",
        "desc": "Looks like you. Moves like you. Copies the last ability you used.",
        "district": 3,
    },
    "Remnant": {
        "name": "Remnant",
        "hp": 60, "max_hp": 60,
        "atk": 18, "defense": 999,
        "gold": 18, "xp": 45,
        "color": (100, 100, 255),
        "special": "immune_physical",
        "desc": "Pure energy. Physical attacks pass through it.",
        "district": 3,
    },
}

BOSSES = {
    "The First Crack": {
        "name": "The First Crack",
        "hp": 350, "max_hp": 350,
        "atk": 45, "defense": 15,
        "gold": 200, "xp": 300,
        "color": (80, 60, 100),
        "special": "regen",
        "regen_amount": 8,
        "suppress_threshold": 0.15,
        "drops": ["Warden's Seal"],
        "desc": "Something sealed beneath the Undercroft ten years ago. It waited.",
        "district": 1,
    },
    "The Broker": {
        "name": "The Broker",
        "hp": 280, "max_hp": 280,
        "atk": 0, "defense": 20,
        "gold": 300, "xp": 350,
        "color": (160, 120, 40),
        "special": "summon",
        "summon_type": "Debt Collector",
        "max_summons": 2,
        "drops": ["Broker's Coin"],
        "desc": "Made a deal with what came through the cracks. Became part of the deal.",
        "district": 2,
    },
    "The Last Captain": {
        "name": "The Last Captain",
        "hp": 400, "max_hp": 400,
        "atk": 52, "defense": 22,
        "gold": 400, "xp": 500,
        "color": (180, 160, 120),
        "special": "warden_abilities",
        "drops": ["Captain's Blade"],
        "desc": "Your predecessor. Sealed himself in as penance. He doesn't want to fight.",
        "district": 3,
        "can_talk": True,
    },
}

def get_enemy(name):
    if name in ENEMIES:
        e = dict(ENEMIES[name])
        e["hp"] = e["max_hp"]
        return e
    if name in BOSSES:
        b = dict(BOSSES[name])
        b["hp"] = b["max_hp"]
        return b
    return None

def random_enemy_for_district(district):
    pool = [e for e in ENEMIES.values() if e["district"] == district]
    if not pool:
        return None
    chosen = dict(random.choice(pool))
    chosen["hp"] = chosen["max_hp"]
    return chosen
