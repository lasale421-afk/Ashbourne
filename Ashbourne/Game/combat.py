import pygame
import random
from logic import (calculate_damage, calculate_magic_damage, apply_buff, tick_buffs,
                   get_effective_atk, get_effective_magic, gain_xp, apply_item,
                   remove_from_inventory, get_unlocked_abilities, get_unlocked_spells,
                   ABILITIES, SPELLS)
from ui import draw_hp_bar, draw_text, FloatingText
from i18n import get as _

# Combat states
CS_PLAYER_TURN  = "player_turn"
CS_ENEMY_TURN   = "enemy_turn"
CS_ANIMATING    = "animating"
CS_VICTORY      = "victory"
CS_DEFEAT       = "defeat"
CS_FLED         = "fled"

MENU_MAIN   = "main"
MENU_ITEMS  = "items"
MENU_SKILLS = "skills"
MENU_SPELLS = "spells"


class CombatManager:
    def __init__(self, font_small, font_med, font_large, screen_w, screen_h):
        self.fs = font_small
        self.fm = font_med
        self.fl = font_large
        self.sw = screen_w
        self.sh = screen_h
        self.active = False
        self._reset()

    def _reset(self):
        self.player      = None
        self.enemy       = None
        self.state       = CS_PLAYER_TURN
        self.menu        = MENU_MAIN
        self.sel         = 0
        self.log         = []
        self.log_timer   = 0
        self.floats      = FloatingText()
        self.flash_timer = 0
        self.flash_color = None
        self.anim_timer  = 0
        self.anim_msg    = ""
        self.ability_used_single = set()
        self.turn_count  = 0
        self.on_victory  = None
        self.on_defeat   = None
        self.on_fled     = None
        self.summons     = []
        self.enemy_suppressed = False
        self.enemy_ability_cooldowns = {"Counter": 0, "War Cry": 0, "Last Stand": 0}
        self.progress    = {}

    def start(self, player, enemy_data, progress, on_victory=None, on_defeat=None, on_fled=None):
        self._reset()
        self.player     = player
        self.enemy      = dict(enemy_data)
        self.enemy["hp"] = self.enemy.get("hp", self.enemy.get("max_hp", 100))
        self.progress   = progress
        self.on_victory = on_victory
        self.on_defeat  = on_defeat
        self.on_fled    = on_fled
        self.active     = True
        # Reset per-combat state on player
        self.player["combat_buffs"] = []
        self.player["ability_cooldowns"] = {}
        self.ability_used_single = set()
        # Crawlers go first
        if self.enemy.get("special") == "first":
            self.state = CS_ENEMY_TURN
            self._log(_("combat_log_first", self.enemy['name']))
        else:
            self.state = CS_PLAYER_TURN
        self._log(_("combat_log_encounter", self.enemy['name']))

    def handle_input(self, event):
        if not self.active or self.state not in (CS_PLAYER_TURN,):
            return
        if event.type != pygame.KEYDOWN:
            return

        unlocked = get_unlocked_abilities(self.progress)

        if self.menu == MENU_MAIN:
            options = [_("combat_attack"), _("combat_skills"), _("combat_spells"), _("combat_items"), _("combat_flee")]
            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(options)
            elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                choice = options[self.sel]
                if choice == _("combat_attack"):
                    self._player_attack()
                elif choice == _("combat_skills"):
                    self.menu = MENU_SKILLS
                    self.sel = 0
                elif choice == _("combat_spells"):
                    self.menu = MENU_SPELLS
                    self.sel = 0
                elif choice == _("combat_items"):
                    self.menu = MENU_ITEMS
                    self.sel = 0
                elif choice == _("combat_flee"):
                    self._player_flee()
            elif event.key == pygame.K_ESCAPE:
                pass

        elif self.menu == MENU_ITEMS:
            inv = self.player["inventory"]
            usable = [i for i in inv if i["type"] in ("heal", "mana", "escape")]
            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel = max(0, self.sel - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = min(len(usable) - 1 if usable else 0, self.sel + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_e):
                if usable and 0 <= self.sel < len(usable):
                    item = usable[self.sel]
                    result = apply_item(self.player, item)
                    idx = self.player["inventory"].index(item)
                    remove_from_inventory(self.player, idx)
                    if result == "ESCAPE":
                        self._player_flee(force=True)
                    else:
                        self._log(_("combat_log_used_item", item['name'], result))
                        self._flash((60, 200, 60))
                        self.menu = MENU_MAIN
                        self.sel = 0
                        self._start_enemy_turn()
            elif event.key in (pygame.K_ESCAPE, pygame.K_i):
                self.menu = MENU_MAIN
                self.sel = 0

        elif self.menu == MENU_SKILLS:
            cd = self.player.get("ability_cooldowns", {})
            available = []
            for ab in unlocked:
                data = ABILITIES[ab]
                single = data.get("single_use") and ab in self.ability_used_single
                on_cd  = cd.get(ab, 0) > 0
                available.append((ab, data, single, on_cd))

            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel = max(0, self.sel - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = min(len(available) - 1 if available else 0, self.sel + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_e):
                if available and 0 <= self.sel < len(available):
                    ab, data, single, on_cd = available[self.sel]
                    if single or on_cd:
                        self._log(_("combat_not_available"))
                    else:
                        self._use_ability(ab, data)
            elif event.key in (pygame.K_ESCAPE,):
                self.menu = MENU_MAIN
                self.sel = 0

        elif self.menu == MENU_SPELLS:
            spells = get_unlocked_spells(self.progress)
            mp = self.player.get("mp", 0)
            available = []
            for sp in spells:
                data = SPELLS[sp]
                enough = mp >= data["mp_cost"]
                available.append((sp, data, enough))

            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel = max(0, self.sel - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = min(len(available) - 1 if available else 0, self.sel + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_e):
                if available and 0 <= self.sel < len(available):
                    sp, data, enough = available[self.sel]
                    if not enough:
                        self._log(_("combat_not_enough_mp"))
                    else:
                        self._cast_spell(sp, data)
            elif event.key in (pygame.K_ESCAPE,):
                self.menu = MENU_MAIN
                self.sel = 0

    def _log(self, msg):
        self.log.append(msg)
        if len(self.log) > 6:
            self.log.pop(0)

    def _flash(self, color, duration=0.2):
        self.flash_color = color
        self.flash_timer = duration

    def _tick_player_cooldowns(self):
        cd = self.player.get("ability_cooldowns", {})
        for ab in list(cd.keys()):
            if cd[ab] > 0:
                cd[ab] -= 1
        self.player["ability_cooldowns"] = cd

    def _player_attack(self):
        dmg = calculate_damage(get_effective_atk(self.player), self.enemy.get("defense", 0))
        # Last Stand
        cd = self.player.get("ability_cooldowns", {})
        if ("Last Stand" in get_unlocked_abilities(self.progress)
                and "Last Stand" in self.ability_used_single  # not consumed yet
                and self.player["hp"] / self.player["max_hp"] < 0.3):
            dmg *= 3

        # Check immune
        if self.enemy.get("special") == "immune_physical":
            self._log(_("combat_log_immune", self.enemy['name']))
            self._flash((100, 100, 200))
            self._start_enemy_turn()
            return

        self.enemy["hp"] = max(0, self.enemy["hp"] - dmg)
        self._log(_("combat_log_damage", dmg, self.enemy['name']))
        self._flash((200, 60, 60))
        self.floats.add(f"-{dmg}", self.sw // 2 + 120, self.sh // 2 - 40, (255, 80, 80))

        # Suppression for First Crack
        if self.enemy.get("special") == "regen":
            if dmg > self.enemy["max_hp"] * self.enemy.get("suppress_threshold", 0.15):
                self.enemy_suppressed = True
                self._log(_("combat_log_suppress", self.enemy['name']))

        if self.enemy["hp"] <= 0:
            self._resolve_victory()
        else:
            self._start_enemy_turn()

    def _use_ability(self, name, data):
        cd = self.player.get("ability_cooldowns", {})
        if data.get("single_use"):
            self.ability_used_single.add(name)

        if name == "Counter":
            self._log(_("combat_counter"))
            self.player["_counter"] = True
            cd["Counter"] = data["cooldown"]
            self.player["ability_cooldowns"] = cd
            self._start_enemy_turn()

        elif name == "War Cry":
            apply_buff(self.player, "atk", 6, 3)
            self._log(_("combat_war_cry"))
            self._flash((220, 180, 40))
            cd["War Cry"] = data["cooldown"]
            self.player["ability_cooldowns"] = cd
            self._start_enemy_turn()

        elif name == "Last Stand":
            self._log(_("combat_last_stand"))
            self.ability_used_single.add("Last Stand")
            cd["Last Stand"] = data["cooldown"]
            self.player["ability_cooldowns"] = cd
            self.menu = MENU_MAIN
            self.sel = 0

        elif name == "Warden's Oath":
            heal = int(self.player["max_hp"] * 0.25)
            self.player["hp"] = min(self.player["hp"] + heal, self.player["max_hp"])
            self._log(_("combat_warden", heal))
            self._flash((60, 200, 60))
            self.ability_used_single.add("Warden's Oath")
            self.menu = MENU_MAIN
            self.sel = 0

    def _cast_spell(self, name, data):
        cost = data["mp_cost"]
        self.player["mp"] = max(0, self.player["mp"] - cost)
        power = data["power"]
        magic = get_effective_magic(self.player)
        dmg = calculate_magic_damage(power + magic)
        self.enemy["hp"] = max(0, self.enemy["hp"] - dmg)
        self._log(_("combat_cast", name, dmg))
        self._flash((120, 80, 200))
        self.floats.add(f"-{dmg}", self.sw // 2 + 120, self.sh // 2 - 40, (180, 80, 255))
        if self.enemy["hp"] <= 0:
            self._resolve_victory()
        else:
            self._start_enemy_turn()

    def _start_enemy_turn(self):
        self.state = CS_ENEMY_TURN
        self.anim_timer = 0.5
        self.menu = MENU_MAIN
        self.sel = 0
        tick_buffs(self.player)
        self._tick_player_cooldowns()

    def _do_enemy_turn(self):
        enemy = self.enemy
        special = enemy.get("special")
        player = self.player

        # Regen
        if special == "regen" and not self.enemy_suppressed:
            regen = enemy.get("regen_amount", 8)
            enemy["hp"] = min(enemy["hp"] + regen, enemy["max_hp"])
            self._log(_("combat_log_regen", enemy['name'], regen))
        self.enemy_suppressed = False

        # Summon (Broker)
        if special == "summon":
            if len(self.summons) < enemy.get("max_summons", 2):
                from data.enemies import get_enemy
                summon = get_enemy(enemy.get("summon_type", "Debt Collector"))
                if summon:
                    self.summons.append(summon)
                    self._log(_("combat_log_summon", enemy['name'], summon['name']))
            # Summons attack
            for s in self.summons:
                if s["hp"] > 0:
                    dmg = calculate_damage(s["atk"], player["defense"])
                    player["hp"] = max(0, player["hp"] - dmg)
                    self._log(_("combat_log_summon_dmg", s['name'], dmg))
            self._check_player_defeat()
            self.state = CS_PLAYER_TURN
            self.turn_count += 1
            return

        # Captain abilities
        if special == "warden_abilities":
            self._enemy_warden_attack()
            return

        # Normal attack
        raw_dmg = calculate_damage(enemy["atk"], player["defense"])
        counter = player.pop("_counter", False)
        if counter:
            raw_dmg = max(1, raw_dmg // 2)
            counter_dmg = calculate_damage(get_effective_atk(player), enemy["defense"])
            enemy["hp"] = max(0, enemy["hp"] - counter_dmg)
            self._log(_("combat_log_counter", enemy['name'], raw_dmg, counter_dmg))
            self.floats.add(f"-{counter_dmg}", self.sw // 2 + 120, self.sh // 2 - 40, (255, 80, 80))
        else:
            self._log(_("combat_log_enemy", enemy['name'], raw_dmg))

        player["hp"] = max(0, player["hp"] - raw_dmg)
        self._flash((60, 60, 200))
        self.floats.add(f"-{raw_dmg}", self.sw // 2 - 160, self.sh // 2 - 40, (80, 80, 255))

        # Steal gold
        if special == "steal":
            stolen = min(10, player["gold"])
            player["gold"] -= stolen
            if stolen > 0:
                self._log(_("combat_log_steal", enemy['name'], stolen))

        # Echo mirrors last ability  
        if special == "mirror":
            self._log(_("combat_log_mirror", enemy['name']))

        if enemy["hp"] <= 0:
            self._resolve_victory()
            return

        self._check_player_defeat()
        self.state = CS_PLAYER_TURN
        self.turn_count += 1

    def _enemy_warden_attack(self):
        enemy = self.enemy
        player = self.player
        ecd = self.enemy_ability_cooldowns
        roll = random.random()

        if ecd.get("Counter", 0) <= 0 and roll < 0.3:
            self._log(_("combat_log_enemy_counter", enemy['name']))
            enemy["_counter"] = True
            ecd["Counter"] = 3
        elif ecd.get("War Cry", 0) <= 0 and roll < 0.5:
            enemy["atk"] = enemy.get("atk", 52) + 6
            self._log(_("combat_log_enemy_war_cry", enemy['name']))
            ecd["War Cry"] = 4
        else:
            raw_dmg = calculate_damage(enemy["atk"], player["defense"])
            counter = player.pop("_counter", False)
            if counter:
                raw_dmg = max(1, raw_dmg // 2)
                counter_dmg = calculate_damage(get_effective_atk(player), enemy["defense"])
                enemy["hp"] = max(0, enemy["hp"] - counter_dmg)
                self._log(_("combat_log_counter", enemy['name'], raw_dmg, counter_dmg))
            else:
                self._log(_("combat_log_enemy", enemy['name'], raw_dmg))
            player["hp"] = max(0, player["hp"] - raw_dmg)
            self._flash((60, 60, 200))

        for k in ecd:
            if ecd[k] > 0:
                ecd[k] -= 1

        if enemy["hp"] <= 0:
            self._resolve_victory()
            return
        self._check_player_defeat()
        self.state = CS_PLAYER_TURN
        self.turn_count += 1

    def _player_flee(self, force=False):
        if force or random.random() < 0.6:
            self._log(_("combat_flee"))
            self.state = CS_FLED
            self.active = False
            if self.on_fled:
                self.on_fled()
        else:
            self._log(_("combat_flee_fail"))
            self._start_enemy_turn()

    def _resolve_victory(self):
        enemy  = self.enemy
        player = self.player
        gold_bonus = player.get("gold_bonus", 1.0)
        gold_earned = int(enemy.get("gold", 0) * gold_bonus)
        player["gold"] += gold_earned
        district = enemy.get("district", 0)
        leveled, xp_earned = gain_xp(player, enemy.get("xp", 0), district)
        msg = _("combat_victory_msg", enemy['name'], xp_earned, gold_earned)
        if leveled:
            msg += _("combat_level_up", player['level'])
        self._log(msg)
        self.state = CS_VICTORY
        self.active = False
        if self.on_victory:
            drops = enemy.get("drops", [])
            self.on_victory(enemy["name"], drops, leveled)

    def _check_player_defeat(self):
        if self.player["hp"] <= 0:
            self._log(_("combat_fallen"))
            self.state = CS_DEFEAT
            self.active = False
            if self.on_defeat:
                self.on_defeat()

    def update(self, dt):
        if not self.active and self.state not in (CS_VICTORY, CS_DEFEAT, CS_FLED):
            return
        self.floats.update(dt)
        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.state == CS_ENEMY_TURN:
            self.anim_timer -= dt
            if self.anim_timer <= 0:
                self._do_enemy_turn()

    def draw(self, surface, bg_surface):
        # Solid black background — no overworld artifacts
        surface.fill((8, 6, 4))

        # Screen flash
        if self.flash_timer > 0 and self.flash_color:
            f = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
            alpha = int(120 * (self.flash_timer / 0.2))
            f.fill((*self.flash_color, min(120, alpha)))
            surface.blit(f, (0, 0))

        panel_y = 70
        panel_h = self.sh - 160

        # ── Player panel (left) ───────────────────────────────────────────
        pp_w, pp_h = 220, 200
        pp_x, pp_y = 30, panel_y + (panel_h - pp_h) // 2
        pp_bg = pygame.Surface((pp_w, pp_h), pygame.SRCALPHA)
        pp_bg.fill((10, 8, 6, 210))
        surface.blit(pp_bg, (pp_x, pp_y))
        pygame.draw.rect(surface, (100, 90, 70), (pp_x, pp_y, pp_w, pp_h), 2)

        player = self.player
        draw_text(surface, player["name"], pp_x + 10, pp_y + 10,
                  self.fm, (210, 185, 130))
        draw_text(surface, f"{_('combat_stats_level')} {player['level']}",
                  pp_x + 10, pp_y + 32, self.fs, (160, 150, 120))
        draw_text(surface, f"{_('combat_stats_hp')}  {player['hp']} / {player['max_hp']}",
                  pp_x + 10, pp_y + 56, self.fs, (180, 160, 130))
        draw_hp_bar(surface, pp_x + 10, pp_y + 74, player["hp"], player["max_hp"],
                    width=pp_w - 20, height=12)
        draw_text(surface, f"{_('combat_stats_mp')}  {player.get('mp', 0)} / {player.get('max_mp', 0)}",
                  pp_x + 10, pp_y + 92, self.fs, (140, 160, 200))
        draw_hp_bar(surface, pp_x + 10, pp_y + 110, player.get("mp", 0), player.get("max_mp", 0),
                    width=pp_w - 20, height=8, fill=(60, 100, 180), bg=(20, 30, 50))
        draw_text(surface, f"{_('combat_stats_atk')} {player['atk']}  {_('combat_stats_def')} {player['defense']}  {_('combat_stats_mag')} {player.get('magic', 10)}",
                  pp_x + 10, pp_y + 124, self.fs, (160, 150, 120))

        # Ability cooldowns
        unlocked = get_unlocked_abilities(self.progress)
        cd = player.get("ability_cooldowns", {})
        cy = pp_y + 120
        draw_text(surface, _("combat_player"), pp_x + 10, cy, self.fs, (130, 120, 100))
        cy += 18
        for ab in unlocked:
            single = ABILITIES[ab].get("single_use") and ab in self.ability_used_single
            on_cd  = cd.get(ab, 0) > 0
            if single:
                col = (80, 80, 80)
                label = f"  {ab}  [used]"
            elif on_cd:
                col = (120, 100, 80)
                label = f"  {ab}  [cd:{cd[ab]}]"
            else:
                col = (180, 200, 140)
                label = f"  {ab}"
            draw_text(surface, label, pp_x + 10, cy, self.fs, col)
            cy += 18

        # Buffs
        if player.get("combat_buffs"):
            for buff in player["combat_buffs"]:
                draw_text(surface, f"  +{buff['value']} {buff['type']} ({buff['duration']}{_('combat_stats_turn')})",
                          pp_x + 10, cy, self.fs, (200, 180, 80))
                cy += 16

        # ── Enemy panel (right) ───────────────────────────────────────────
        ep_w, ep_h = 220, 200
        ep_x = self.sw - ep_w - 30
        ep_y = panel_y + (panel_h - ep_h) // 2
        ep_bg = pygame.Surface((ep_w, ep_h), pygame.SRCALPHA)
        ep_bg.fill((10, 8, 6, 210))
        surface.blit(ep_bg, (ep_x, ep_y))
        pygame.draw.rect(surface, (100, 70, 70), (ep_x, ep_y, ep_w, ep_h), 2)

        enemy = self.enemy
        draw_text(surface, enemy["name"], ep_x + 10, ep_y + 10,
                  self.fm, (210, 120, 100))
        draw_text(surface, f"{_('combat_stats_hp')}  {enemy['hp']} / {enemy['max_hp']}",
                  ep_x + 10, ep_y + 40, self.fs, (180, 140, 130))
        draw_hp_bar(surface, ep_x + 10, ep_y + 58, enemy["hp"], enemy["max_hp"],
                    width=ep_w - 20, height=12, fill=(180, 40, 40))
        draw_text(surface, f"{_('combat_stats_atk')} {enemy['atk']}  {_('combat_stats_def')} {enemy['defense']}",
                  ep_x + 10, ep_y + 78, self.fs, (160, 130, 120))
        desc = enemy.get("desc", "")
        if desc:
            words = desc.split()
            line, ly = "", ep_y + 104
            for w in words:
                test = line + " " + w if line else w
                if self.fs.size(test)[0] > ep_w - 20:
                    draw_text(surface, line, ep_x + 10, ly, self.fs, (130, 120, 110))
                    line = w
                    ly += 17
                else:
                    line = test
            if line:
                draw_text(surface, line, ep_x + 10, ly, self.fs, (130, 120, 110))

        # Summons display
        if self.summons:
            sy = ep_y + ep_h + 8
            for s in self.summons:
                if s["hp"] > 0:
                    draw_text(surface, f"  {s['name']}  {_('combat_stats_hp')}:{s['hp']}",
                              ep_x, sy, self.fs, (180, 130, 80))
                    sy += 18

        # ── Enemy sprite (center) ─────────────────────────────────────────
        cx = self.sw // 2
        cy_mid = panel_y + panel_h // 2
        ec = enemy.get("color", (180, 80, 80))
        is_boss = enemy.get("is_boss") or enemy["name"] in ("The First Crack",
                                                              "The Broker",
                                                              "The Last Captain")
        ew = 80 if is_boss else 50
        eh = 80 if is_boss else 50
        ex = cx - ew // 2
        ey = cy_mid - eh // 2
        pygame.draw.rect(surface, ec, (ex, ey, ew, eh))
        if is_boss:
            pygame.draw.rect(surface, (255, 255, 255), (ex, ey, ew, eh), 2)

        # Player sprite intentionally omitted — UI panels only

        # ── Combat log ────────────────────────────────────────────────────
        log_y = self.sh - 130
        log_bg = pygame.Surface((self.sw - 60, 70), pygame.SRCALPHA)
        log_bg.fill((8, 6, 4, 200))
        surface.blit(log_bg, (30, log_y))
        pygame.draw.rect(surface, (80, 70, 55), (30, log_y, self.sw - 60, 70), 1)
        for i, line in enumerate(self.log[-3:]):
            alpha_idx = i
            col = (200, 195, 185) if alpha_idx == 2 else (140, 130, 110)
            draw_text(surface, line, 42, log_y + 6 + i * 20, self.fs, col)

        # ── Menu (bottom) ─────────────────────────────────────────────────
        menu_y = self.sh - 52
        if self.state == CS_PLAYER_TURN:
            self._draw_menu(surface, menu_y)
        elif self.state == CS_VICTORY:
            draw_text(surface, _("combat_victory"), self.sw // 2 - 100,
                      menu_y + 10, self.fm, (200, 200, 100))
        elif self.state == CS_DEFEAT:
            draw_text(surface, _("combat_defeat"), self.sw // 2 - 110,
                      menu_y + 10, self.fm, (200, 80, 80))

        # Floating numbers
        self.floats.draw(surface, self.fs)

    def _draw_menu(self, surface, y):
        bg = pygame.Surface((self.sw - 60, 45), pygame.SRCALPHA)
        bg.fill((10, 8, 6, 210))
        surface.blit(bg, (30, y))
        pygame.draw.rect(surface, (80, 70, 55), (30, y, self.sw - 60, 45), 1)

        if self.menu == MENU_MAIN:
            options = [_("combat_attack"), _("combat_skills"), _("combat_items"), _("combat_flee")]
            x = 50
            for i, opt in enumerate(options):
                col = (220, 200, 120) if i == self.sel else (140, 130, 110)
                prefix = "> " if i == self.sel else "  "
                w = draw_text(surface, prefix + opt, x, y + 12, self.fm, col)
                x += w + 40

        elif self.menu == MENU_ITEMS:
            inv = self.player["inventory"]
            usable = [i for i in inv if i["type"] in ("heal", "escape")]
            draw_text(surface, _("combat_item_label"), 50, y + 6, self.fs, (160, 150, 120))
            if not usable:
                draw_text(surface, _("combat_no_items"), 150, y + 6,
                          self.fs, (100, 95, 85))
            else:
                x = 150
                for i, item in enumerate(usable):
                    col = (220, 200, 120) if i == self.sel else (140, 130, 110)
                    prefix = "> " if i == self.sel else ""
                    w = draw_text(surface, prefix + item["name"], x, y + 6,
                                  self.fs, col)
                    x += w + 20
            draw_text(surface, _("combat_esc"), 50, y + 26, self.fs, (80, 75, 65))

        elif self.menu == MENU_SKILLS:
            unlocked = get_unlocked_abilities(self.progress)
            cd = self.player.get("ability_cooldowns", {})
            draw_text(surface, _("combat_ability"), 50, y + 6, self.fs, (160, 150, 120))
            x = 150
            for i, ab in enumerate(unlocked):
                single = ABILITIES[ab].get("single_use") and ab in self.ability_used_single
                on_cd  = cd.get(ab, 0) > 0
                col = (80, 80, 80) if (single or on_cd) else \
                      (220, 200, 120) if i == self.sel else (140, 130, 110)
                prefix = "> " if i == self.sel else ""
                label = ab + (f"[{cd[ab]}]" if on_cd else "") + ("[U]" if single else "")
                w = draw_text(surface, prefix + label, x, y + 6, self.fs, col)
                x += w + 16
            draw_text(surface, _("combat_esc"), 50, y + 26, self.fs, (80, 75, 65))

        elif self.menu == MENU_SPELLS:
            spells = get_unlocked_spells(self.progress)
            mp = self.player.get("mp", 0)
            draw_text(surface, _("combat_spell"), 50, y + 6, self.fs, (160, 150, 120))
            x = 150
            for i, sp in enumerate(spells):
                data = SPELLS[sp]
                enough = mp >= data["mp_cost"]
                col = (80, 80, 80) if not enough else \
                      (220, 200, 120) if i == self.sel else (140, 130, 110)
                prefix = "> " if i == self.sel else ""
                label = f"{sp} ({data['mp_cost']} MP)"
                w = draw_text(surface, prefix + label, x, y + 6, self.fs, col)
                x += w + 16
            draw_text(surface, _("combat_esc"), 50, y + 26, self.fs, (80, 75, 65))
