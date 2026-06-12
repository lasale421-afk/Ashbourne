import random

# ── Damage ──────────────────────────────────────────────────────────────────

def calculate_damage(atk, defense, variance=0.15):
    base = max(1, atk - defense)
    spread = int(base * variance)
    return max(1, base + random.randint(-spread, spread))


def calculate_magic_damage(magic_atk, magic_def=0, variance=0.15):
    base = max(1, magic_atk - magic_def)
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

SPELLS = {
    "Ember": {
        "name": "Ember",
        "desc": "Small fire bolt. 8 MP.",
        "mp_cost": 8,
        "power": 25,
        "element": "fire",
        "unlock": "start",
    },
    "Arcane Bolt": {
        "name": "Arcane Bolt",
        "desc": "Piercing magic. 12 MP.",
        "mp_cost": 12,
        "power": 40,
        "element": "arcane",
        "unlock": "district_1",
    },
    "Soul Flame": {
        "name": "Soul Flame",
        "desc": "Heavy magic. 20 MP.",
        "mp_cost": 20,
        "power": 70,
        "element": "fire",
        "unlock": "district_2",
    },
    "Void Tear": {
        "name": "Void Tear",
        "desc": "Devastating magic. 30 MP.",
        "mp_cost": 30,
        "power": 110,
        "element": "arcane",
        "unlock": "district_3",
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


def get_unlocked_spells(progress):
    unlocked = ["Ember"]
    if progress.get("district_1_done"):
        unlocked.append("Arcane Bolt")
    if progress.get("district_2_done"):
        unlocked.append("Soul Flame")
    if progress.get("district_3_done"):
        unlocked.append("Void Tear")
    return unlocked


def get_effective_magic(player):
    return player.get("magic", 10) + player.get("level", 1) * 2


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
    player["hp"] = player["max_hp"]  # full heal on level up
    player["max_mp"] += 8
    player["mp"] = player["max_mp"]  # full mana on level up
    player["atk"] += 2
    player["magic"] += 2
    player["defense"] += 1


# ── Items ────────────────────────────────────────────────────────────────────

def apply_item(player, item):
    from i18n import get as _
    itype = item.get("type")
    val = item.get("value", 0)
    if itype == "heal":
        old = player["hp"]
        player["hp"] = min(player["hp"] + val, player["max_hp"])
        return _("notify_item_healed", player['hp'] - old)
    elif itype == "mana":
        old = player.get("mp", 0)
        player["mp"] = min(player["mp"] + val, player["max_mp"])
        return _("notify_item_mana", player['mp'] - old)
    elif itype == "atk":
        player["atk"] += val
        return _("notify_item_atk", val)
    elif itype == "defense":
        player["defense"] += val
        return _("notify_item_def", val)
    elif itype == "magic":
        player["magic"] = player.get("magic", 10) + val
        return _("notify_item_magic", val)
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
        "mp": 50,
        "max_mp": 50,
        "magic": 12,
        "atk": 16,
        "defense": 10,
        "gold": 50,
        "gold_bonus": 1.0,
        "inventory": [
            dict(ITEMS_POOL[0]),  # Health Potion
            dict(ITEMS_POOL[2]),  # Mana Potion
            dict(ITEMS_POOL[3]),  # Smoke Bomb
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
