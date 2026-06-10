import pygame


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
        draw_text(surface, f"{player['name']}  Lv.{player['level']}",
                  12, 6, self.font_med, (210, 185, 130))

        # HP bar
        hp_txt = f"HP  {player['hp']}/{player['max_hp']}"
        draw_text(surface, hp_txt, 12, 26, self.font_small, (180, 160, 130))
        draw_hp_bar(surface, 90, 28, player["hp"], player["max_hp"],
                    width=140, height=10)

        # XP
        from logic import xp_to_next
        xp_w = 100
        xp_ratio = player["xp"] / xp_to_next(player["level"])
        draw_text(surface, "XP", 250, 26, self.font_small, (100, 140, 180))
        pygame.draw.rect(surface, (20, 30, 50), (274, 28, xp_w, 10))
        pygame.draw.rect(surface, (60, 100, 180),
                         (274, 28, int(xp_w * xp_ratio), 10))
        pygame.draw.rect(surface, (80, 100, 140), (274, 28, xp_w, 10), 1)

        # Gold
        draw_text(surface, f"Gold: {player['gold']}",
                  390, 26, self.font_small, (200, 180, 80))

        # ATK / DEF
        draw_text(surface, f"ATK {player['atk']}",
                  390, 6, self.font_small, (200, 120, 100))
        draw_text(surface, f"DEF {player['defense']}",
                  460, 6, self.font_small, (100, 160, 200))

        # Active quest hint
        steps = quest_manager.active_steps()
        if steps:
            draw_text(surface, steps[0][:60], 12, self.sh - 18,
                      self.font_small, (160, 150, 120))

        # Map name
        mn = map_name.replace("_", " ").title()
        draw_text(surface, mn, self.sw - 180, 6, self.font_small, (130, 120, 100))

        # Controls reminder
        draw_text(surface, "E: interact / I: inventory",
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
                    if item["type"] in ("heal", "atk", "defense"):
                        from logic import apply_item, remove_from_inventory
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

        draw_text(surface, "INVENTORY", px + 12, py + 10,
                  self.font_med, (210, 185, 130))
        draw_text(surface, f"Gold: {player['gold']}",
                  px + pw - 120, py + 10, self.font_small, (200, 180, 80))

        inv = player["inventory"]
        if not inv:
            draw_text(surface, "(empty)", px + 12, py + 50,
                      self.font_small, (100, 95, 85))
        for i, item in enumerate(inv):
            y_pos = py + 50 + i * 24
            color = (220, 200, 130) if i == self.sel else (160, 155, 140)
            prefix = "> " if i == self.sel else "  "
            itype_label = {"heal": "HP", "atk": "ATK", "defense": "DEF",
                           "escape": "ESC", "lore": "LORE",
                           "gold": "GOLD"}.get(item["type"], "?")
            val_str = f"+{item['value']}" if item["type"] not in ("escape", "lore", "gold") \
                      else ""
            line = f"{prefix}{item['name']}  [{itype_label}{val_str}]"
            draw_text(surface, line, px + 12, y_pos, self.font_small, color)

        draw_text(surface, "ENTER: use   I/ESC: close",
                  px + 12, py + ph - 24, self.font_small, (80, 75, 65))

        # Stats panel
        sx = px + pw + 10
        if sx + 180 < self.sw:
            stats_bg = pygame.Surface((180, ph), pygame.SRCALPHA)
            stats_bg.fill((10, 8, 6, 220))
            surface.blit(stats_bg, (sx, py))
            pygame.draw.rect(surface, (80, 70, 55), (sx, py, 180, ph), 1)
            draw_text(surface, "STATS", sx + 10, py + 10,
                      self.font_med, (210, 185, 130))
            stats = [
                ("HP", f"{player['hp']}/{player['max_hp']}"),
                ("ATK", str(player["atk"])),
                ("DEF", str(player["defense"])),
                ("Level", str(player["level"])),
                ("Gold", str(player["gold"])),
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
