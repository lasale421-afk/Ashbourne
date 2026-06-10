import random

# ── Damage ──────────────────────────────────────────────────────────────────

def calculate_damage(atk, defense, variance=0.15):
    base = max(1, atk - defense)
    spread = int(base * variance)
    return max(1, base + random.randint(-spread, spread))


# ── Abilities ────────────────────────────────────────────────────────────────

ABILITIES = {
    "Counter": {
        "name": "Counter",
        "desc": "Halve incoming damage, deal normal damage back.",
        "cooldown": 3,
        "unlock": "start",
    },
    "War Cry": {
        "name": "War Cry",
        "desc": "+6 ATK for 3 turns.",
        "cooldown": 4,
        "unlock": "district_1",
    },
    "Last Stand": {
        "name": "Last Stand",
        "desc": "Triple damage when HP < 30%.",
        "cooldown": 5,
        "unlock": "district_2",
    },
    "Warden's Oath": {
        "name": "Warden's Oath",
        "desc": "Restore 25% max HP. Single use per combat.",
        "cooldown": 0,
        "unlock": "district_3",
        "single_use": True,
    },
}


def get_unlocked_abilities(progress):
    unlocked = ["Counter"]
    if progress.get("district_1_done"):
        unlocked.append("War Cry")
    if progress.get("district_2_done"):
        unlocked.append("Last Stand")
    if progress.get("district_3_done"):
        unlocked.append("Warden's Oath")
    return unlocked


# ── XP / Leveling ────────────────────────────────────────────────────────────

def xp_to_next(level):
    return int(100 * (level ** 1.5))


def gain_xp(player, amount, district_number=0):
    bonus = 1 + district_number * 0.1
    total = int(amount * bonus)
    player["xp"] += total
    leveled = False
    while player["xp"] >= xp_to_next(player["level"]):
        player["xp"] -= xp_to_next(player["level"])
        level_up(player)
        leveled = True
    return leveled, total


def level_up(player):
    player["level"] += 1
    player["max_hp"] += 15
    player["hp"] = min(player["hp"] + 15, player["max_hp"])
    player["atk"] += 2
    player["defense"] += 1


# ── Items ────────────────────────────────────────────────────────────────────

def apply_item(player, item):
    itype = item.get("type")
    val = item.get("value", 0)
    if itype == "heal":
        old = player["hp"]
        player["hp"] = min(player["hp"] + val, player["max_hp"])
        return f"Restored {player['hp'] - old} HP."
    elif itype == "atk":
        player["atk"] += val
        return f"ATK +{val} (permanent)."
    elif itype == "defense":
        player["defense"] += val
        return f"DEF +{val} (permanent)."
    elif itype == "escape":
        return "ESCAPE"
    elif itype == "gold":
        player["gold_bonus"] = player.get("gold_bonus", 1.0) + 0.5
        return "Passive: +50% gold from kills."
    elif itype == "lore":
        return f"You read: {item.get('desc', '')}"
    return "Nothing happened."


def add_to_inventory(player, item):
    if len(player["inventory"]) < player.get("inv_cap", 12):
        player["inventory"].append(dict(item))
        return True
    return False


def remove_from_inventory(player, index):
    if 0 <= index < len(player["inventory"]):
        return player["inventory"].pop(index)
    return None


# ── Combat helpers ────────────────────────────────────────────────────────────

def new_player(name="Warden"):
    from data.items import ITEMS_POOL
    player = {
        "name": name,
        "level": 1,
        "xp": 0,
        "hp": 150,
        "max_hp": 150,
        "atk": 16,
        "defense": 10,
        "gold": 50,
        "gold_bonus": 1.0,
        "inventory": [
            dict(ITEMS_POOL[0]),  # Health Potion
            dict(ITEMS_POOL[2]),  # Smoke Bomb
        ],
        "inv_cap": 12,
        "ability_cooldowns": {},
        "combat_buffs": [],
    }
    return player


def apply_buff(player, buff_type, value, duration):
    player["combat_buffs"].append({
        "type": buff_type,
        "value": value,
        "duration": duration,
    })
    if buff_type == "atk":
        player["atk"] += value


def tick_buffs(player):
    expired = []
    for buff in player["combat_buffs"]:
        buff["duration"] -= 1
        if buff["duration"] <= 0:
            expired.append(buff)
    for buff in expired:
        player["combat_buffs"].remove(buff)
        if buff["type"] == "atk":
            player["atk"] -= buff["value"]


def get_effective_atk(player):
    return player["atk"]
