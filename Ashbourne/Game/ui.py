import pygame
from i18n import get as _
from logic import xp_to_next
from logic import apply_item, remove_from_inventory
from logic import add_to_inventory
from data.items import MAREN_SHOP



def draw_hp_bar(surface, x, y, current, max_hp, width=120, height=10,
                bg=(60, 20, 20), fill=(180, 40, 40), border=(200, 180, 160)):
    ratio = max(0, min(1, current / max_hp)) if max_hp > 0 else 0
    pygame.draw.rect(surface, bg, (x, y, width, height))
    if ratio > 0:
        fill_color = fill
        if ratio > 0.6:
            fill_color = (40, 160, 40)
        elif ratio > 0.3:
            fill_color = (180, 140, 20)
        pygame.draw.rect(surface, fill_color, (x, y, int(width * ratio), height))
    pygame.draw.rect(surface, border, (x, y, width, height), 1)


def draw_text(surface, text, x, y, font, color=(200, 195, 185), shadow=True):
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        surface.blit(s, (x + 1, y + 1))
    surf = font.render(text, True, color)
    surface.blit(surf, (x, y))
    return surf.get_width()


class HUD:
    def __init__(self, font_small, font_med, screen_w, screen_h):
        self.font_small = font_small
        self.font_med   = font_med
        self.sw = screen_w
        self.sh = screen_h

    def draw(self, surface, player, map_name, quest_manager):
        panel_h = 52
        overlay = pygame.Surface((self.sw, panel_h), pygame.SRCALPHA)
        overlay.fill((8, 6, 4, 200))
        surface.blit(overlay, (0, 0))
        pygame.draw.line(surface, (80, 70, 55), (0, panel_h), (self.sw, panel_h), 1)

        # Name + level
        draw_text(surface, f"{player['name']}  {_('combat_stats_level')}{player['level']}",
                  12, 6, self.font_med, (210, 185, 130))

        # HP bar
        
        hp_txt = f"{_('combat_stats_hp')}  {player['hp']}/{player['max_hp']}"
        draw_text(surface, hp_txt, 12, 26, self.font_small, (180, 160, 130))
        draw_hp_bar(surface, 90, 28, player["hp"], player["max_hp"],
                    width=140, height=10)

        # XP
        
        xp_w = 100
        xp_ratio = player["xp"] / xp_to_next(player["level"])
        draw_text(surface, _("hud_xp"), 250, 26, self.font_small, (100, 140, 180))
        pygame.draw.rect(surface, (20, 30, 50), (274, 28, xp_w, 10))
        pygame.draw.rect(surface, (60, 100, 180),
                         (274, 28, int(xp_w * xp_ratio), 10))
        pygame.draw.rect(surface, (80, 100, 140), (274, 28, xp_w, 10), 1)

        # Gold
        draw_text(surface, f"{_('combat_stats_gold')}: {player['gold']}",
                  390, 26, self.font_small, (200, 180, 80))

        # MP
        mp = player.get("mp", 0)
        max_mp = player.get("max_mp", 0)
        draw_text(surface, f"{_('combat_stats_mp')} {mp}/{max_mp}",
                  530, 6, self.font_small, (140, 160, 220))
        pygame.draw.rect(surface, (20, 30, 50), (530, 26, 80, 8))
        if max_mp > 0:
            pygame.draw.rect(surface, (60, 100, 180),
                             (530, 26, int(80 * mp / max_mp), 8))
        pygame.draw.rect(surface, (80, 100, 140), (530, 26, 80, 8), 1)

        # ATK / DEF / MAG
        draw_text(surface, f"{_('combat_stats_atk')} {player['atk']}",
                  390, 6, self.font_small, (200, 120, 100))
        draw_text(surface, f"{_('combat_stats_def')} {player['defense']}",
                  460, 6, self.font_small, (100, 160, 200))
        draw_text(surface, f"{_('combat_stats_mag')} {player.get('magic', 10)}",
                  620, 6, self.font_small, (180, 120, 200))

        # Active quest hint
        steps = quest_manager.active_steps()
        if steps:
            draw_text(surface, steps[0][:60], 12, self.sh - 18,
                      self.font_small, (160, 150, 120))

        # Map name
        mn = map_name.replace("_", " ").title()
        draw_text(surface, mn, self.sw - 180, 6, self.font_small, (130, 120, 100))

        # Controls reminder
        
        draw_text(surface, _("hud_controls"),
                  self.sw - 210, 26, self.font_small, (80, 75, 65))


class InventoryScreen:
    def __init__(self, font_small, font_med, screen_w, screen_h):
        self.font_small = font_small
        self.font_med   = font_med
        self.sw = screen_w
        self.sh = screen_h
        self.sel = 0
        self.active = False

    def handle_input(self, event, player):
        if not self.active:
            return None
        if event.type == pygame.KEYDOWN:
            inv = player["inventory"]
            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel = max(0, self.sel - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = min(len(inv) - 1 if inv else 0, self.sel + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_e):
                if inv and 0 <= self.sel < len(inv):
                    item = inv[self.sel]
                    if item["type"] in ("heal", "mana", "atk", "defense", "magic"):
                        msg = apply_item(player, item)
                        remove_from_inventory(player, self.sel)
                        self.sel = min(self.sel, len(player["inventory"]) - 1)
                        return ("used", msg)
            elif event.key in (pygame.K_i, pygame.K_ESCAPE):
                self.active = False
        return None

    def draw(self, surface, player):
        if not self.active:
            return
        pw = 360
        ph = 320
        px = (self.sw - pw) // 2
        py = (self.sh - ph) // 2
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((10, 8, 6, 235))
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, (120, 100, 70), (px, py, pw, ph), 2)

        draw_text(surface, _("inv_title"), px + 12, py + 10,
                  self.font_med, (210, 185, 130))
        draw_text(surface, _("inv_gold", player['gold']),
                  px + pw - 120, py + 10, self.font_small, (200, 180, 80))

        inv = player["inventory"]
        if not inv:
            draw_text(surface, _("inv_empty"), px + 12, py + 50,
                      self.font_small, (100, 95, 85))
        for i, item in enumerate(inv):
            y_pos = py + 50 + i * 24
            color = (220, 200, 130) if i == self.sel else (160, 155, 140)
            prefix = "> " if i == self.sel else "  "
            itype_label = {"heal": _("combat_stats_hp"), "atk": _("combat_stats_atk"),
                           "defense": _("combat_stats_def"), "escape": _("combat_esc"), "lore": _("combat_stats_lore"),
                           "gold": _("combat_stats_gold"), "mana": _("combat_stats_mp")}.get(item["type"], "?")
            val_str = f"+{item['value']}" if item["type"] not in ("escape", "lore", "gold") \
                      else ""
            line = f"{prefix}{item['name']}  [{itype_label}{val_str}]"
            draw_text(surface, line, px + 12, y_pos, self.font_small, color)

        draw_text(surface, _("inv_close"),
                  px + 12, py + ph - 24, self.font_small, (80, 75, 65))


class ShopScreen:
    def __init__(self, font_small, font_med, screen_w, screen_h):
        self.fs = font_small
        self.fm = font_med
        self.sw = screen_w
        self.sh = screen_h
        self.sel = 0
        self.active = False

    def handle_input(self, event, player):
        if not self.active:
            return None
        if event.type != pygame.KEYDOWN:
            return None
        items = MAREN_SHOP
        if event.key in (pygame.K_UP, pygame.K_w):
            self.sel = max(0, self.sel - 1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = min(len(items) - 1 if items else 0, self.sel + 1)
        elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
            if items and 0 <= self.sel < len(items):
                item = items[self.sel]
                if player["gold"] >= item["price"]:
                    if add_to_inventory(player, item):
                        player["gold"] -= item["price"]
                        return ("bought", _("notify_item_obtained", item['name']))
                    else:
                        return ("full", _("notify_inv_full"))
                else:
                    return ("poor", _("notify_not_enough_gold"))
        elif event.key in (pygame.K_ESCAPE, pygame.K_i):
            self.active = False
        return None

    def draw(self, surface, player):
        if not self.active:
            return
        
        pw, ph = 420, 360
        px, py = (self.sw - pw) // 2, (self.sh - ph) // 2
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((10, 8, 6, 235))
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, (120, 100, 70), (px, py, pw, ph), 2)

        draw_text(surface, _("shop_title"), px + 12, py + 10,
                  self.fm, (210, 185, 130))
        draw_text(surface, _("shop_gold", player['gold']),
                  px + pw - 140, py + 10, self.fs, (200, 180, 80))

        items = MAREN_SHOP
        for i, item in enumerate(items):
            y = py + 50 + i * 32
            color = (220, 200, 130) if i == self.sel else (160, 155, 140)
            prefix = "> " if i == self.sel else "  "
            itype = item["type"]
            type_label = {"heal": _("combat_stats_hp"), "mana": _("combat_stats_mp"), "escape": _("combat_esc"),
                          "atk": _("combat_stats_atk"), "defense": _("combat_stats_def"),
                          "magic": _("combat_stats_mag")}.get(itype, "?")
            val_str = f" +{item['value']}" if itype not in ("escape", "lore", "gold") else ""
            line = f"{prefix}{item['name']}{val_str} [{type_label}] — {item['price']}g"
            draw_text(surface, line, px + 12, y, self.fs, color)

        draw_text(surface, _("shop_buy"),
                  px + 12, py + ph - 24, self.fs, (80, 75, 65))

        # Stats panel
        sx = px + pw + 10
        if sx + 180 < self.sw:
            stats_bg = pygame.Surface((180, ph), pygame.SRCALPHA)
            stats_bg.fill((10, 8, 6, 220))
            surface.blit(stats_bg, (sx, py))
            pygame.draw.rect(surface, (80, 70, 55), (sx, py, 180, ph), 1)
            draw_text(surface, _("shop_stats"), sx + 10, py + 10,
                      self.font_med, (210, 185, 130))
            stats = [
                (_("combat_stats_hp"), f"{player['hp']}/{player['max_hp']}"),
                (_("combat_stats_mp"), f"{player.get('mp', 0)}/{player.get('max_mp', 0)}"),
                (_("combat_stats_atk"), str(player["atk"])),
                (_("combat_stats_def"), str(player["defense"])),
                (_("combat_stats_mag"), str(player.get("magic", 10))),
                (_("combat_stats_level"), str(player["level"])),
                (_("combat_stats_gold"), str(player["gold"])),
            ]
            for j, (k, v) in enumerate(stats):
                draw_text(surface, f"{k}:", sx + 10, py + 40 + j * 22,
                          self.font_small, (140, 130, 110))
                draw_text(surface, v, sx + 80, py + 40 + j * 22,
                          self.font_small, (200, 195, 180))


class FloatingText:
    def __init__(self):
        self.items = []

    def add(self, text, x, y, color=(255, 200, 100), duration=1.2):
        self.items.append({
            "text": text, "x": x, "y": y, "color": color,
            "timer": duration, "max_dur": duration
        })

    def update(self, dt):
        for item in self.items:
            item["timer"] -= dt
            item["y"] -= 30 * dt
        self.items = [i for i in self.items if i["timer"] > 0]

    def draw(self, surface, font, cam_x=0, cam_y=0):
        for item in self.items:
            alpha = int(255 * (item["timer"] / item["max_dur"]))
            col = (*item["color"][:3],)
            surf = font.render(item["text"], True, col)
            surf.set_alpha(alpha)
            surface.blit(surf, (item["x"] - cam_x, item["y"] - cam_y))


class NotificationBar:
    def __init__(self, font_small, screen_w, screen_h):
        self.font = font_small
        self.sw = screen_w
        self.sh = screen_h
        self.queue = []
        self.current = None
        self.timer = 0

    def push(self, msg, color=(200, 195, 185), duration=2.5):
        self.queue.append({"msg": msg, "color": color, "duration": duration})

    def update(self, dt):
        if self.current:
            self.timer -= dt
            if self.timer <= 0:
                self.current = None
        if not self.current and self.queue:
            self.current = self.queue.pop(0)
            self.timer = self.current["duration"]

    def draw(self, surface):
        if not self.current:
            return
        msg = self.current["msg"]
        surf = self.font.render(msg, True, self.current["color"])
        x = (self.sw - surf.get_width()) // 2
        y = self.sh - 60
        bg = pygame.Surface((surf.get_width() + 20, 24), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surface.blit(bg, (x - 10, y - 2))
        surface.blit(surf, (x, y))


class PauseMenuScreen:
    def __init__(self, font_small, font_med, screen_w, screen_h):
        self.fs = font_small
        self.fm = font_med
        self.sw = screen_w
        self.sh = screen_h
        self.sel = 0
        self.active = False
        self.options = ["resume", "options", "save", "quit"]

    def handle_input(self, event):
        if not self.active:
            return None
        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_UP, pygame.K_w):
            self.sel = max(0, self.sel - 1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = min(len(self.options) - 1, self.sel + 1)
        elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
            return self.options[self.sel]
        elif event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self.active = False
            return "resume"
        return None

    def draw(self, surface):
        if not self.active:
            return
        pw, ph = 340, 300
        px, py = (self.sw - pw) // 2, (self.sh - ph) // 2
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((10, 8, 6, 235))
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, (120, 100, 70), (px, py, pw, ph), 2)

        draw_text(surface, _("pause_title"), px + 12, py + 10,
                  self.fm, (210, 185, 130))

        labels = {
            "resume": _("pause_resume"),
            "options": _("pause_options"),
            "save": _("pause_save"),
            "quit": _("pause_quit"),
        }
        for i, opt in enumerate(self.options):
            y = py + 60 + i * 44
            color = (220, 200, 130) if i == self.sel else (160, 155, 140)
            prefix = "> " if i == self.sel else "  "
            draw_text(surface, f"{prefix}{labels[opt]}", px + 12, y,
                      self.fm, color)

        draw_text(surface, _("combat_esc"), px + 12, py + ph - 24,
                  self.fs, (80, 75, 65))


class OptionsScreen:
    def __init__(self, font_small, font_med, screen_w, screen_h):
        self.fs = font_small
        self.fm = font_med
        self.sw = screen_w
        self.sh = screen_h
        self.sel = 0
        self.active = False
        self.options = ["language", "brightness", "return"]
        self.langs = ["en", "fr", "es"]
        self.lang_sel = 0
        self.brightness = 1.0

    def handle_input(self, event):
        if not self.active:
            return None
        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_UP, pygame.K_w):
            self.sel = max(0, self.sel - 1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = min(len(self.options) - 1, self.sel + 1)
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            if self.options[self.sel] == "language":
                self.lang_sel = max(0, self.lang_sel - 1)
                return ("lang", self.langs[self.lang_sel])
            elif self.options[self.sel] == "brightness":
                self.brightness = max(0.3, round(self.brightness - 0.1, 1))
                return ("brightness", self.brightness)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            if self.options[self.sel] == "language":
                self.lang_sel = min(len(self.langs) - 1, self.lang_sel + 1)
                return ("lang", self.langs[self.lang_sel])
            elif self.options[self.sel] == "brightness":
                self.brightness = min(1.5, round(self.brightness + 0.1, 1))
                return ("brightness", self.brightness)
        elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
            if self.options[self.sel] == "return":
                self.active = False
                return "return"
        elif event.key == pygame.K_ESCAPE:
            self.active = False
            return "return"
        return None

    def draw(self, surface):
        if not self.active:
            return
        pw, ph = 400, 260
        px, py = (self.sw - pw) // 2, (self.sh - ph) // 2
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((10, 8, 6, 235))
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, (120, 100, 70), (px, py, pw, ph), 2)

        draw_text(surface, _("options_title"), px + 12, py + 10,
                  self.fm, (210, 185, 130))

        lang_labels = {"en": _("options_en"), "fr": _("options_fr"), "es": _("options_es")}
        for i, opt in enumerate(self.options):
            y = py + 60 + i * 50
            color = (220, 200, 130) if i == self.sel else (160, 155, 140)
            prefix = "> " if i == self.sel else "  "
            if opt == "language":
                line = f"{prefix}{_('options_language')}: {lang_labels[self.langs[self.lang_sel]]}"
            elif opt == "brightness":
                bar = "█" * int(self.brightness * 10) + "░" * (15 - int(self.brightness * 10))
                line = f"{prefix}{_('options_brightness')}: {bar}"
            else:
                line = f"{prefix}{_('options_return')}"
            draw_text(surface, line, px + 12, y, self.fm, color)

        draw_text(surface, _("hint_adjust") + "   " + _("combat_esc"), px + 12, py + ph - 24,
                  self.fs, (80, 75, 65))
