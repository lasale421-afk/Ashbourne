import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pygame
from maps import TILE_SIZE, ALL_MAPS, PALETTES
from entities import Player, build_entities
from logic import new_player, apply_item, add_to_inventory
from dialogue import DialogueManager, DIALOGUES
from ui import HUD, InventoryScreen, FloatingText, NotificationBar, draw_text
from combat import CombatManager, CS_VICTORY, CS_DEFEAT, CS_FLED
from data.quests import QuestManager
from data.items import STORY_ITEMS

# ── Constants ─────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 800, 600
FPS = 60
TITLE = "Ashbourne"

# Game states
ST_MENU      = "menu"
ST_NAME_INPUT= "name_input"
ST_OVERWORLD = "overworld"
ST_DIALOGUE  = "dialogue"
ST_COMBAT    = "combat"
ST_INVENTORY = "inventory"
ST_GAMEOVER  = "gameover"
ST_VICTORY   = "victory_screen"


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock   = pygame.time.Clock()

        # Fonts (monospace for dark tone)
        self._init_fonts()

        self.state    = ST_MENU
        self.player   = None
        self.progress = {
            "district_1_done": False,
            "district_2_done": False,
            "district_3_done": False,
            "final_done": False,
            "broker_contact": None,   # "expose" | "silence"
            "captain_talked_down": False,
        }
        self.quests   = QuestManager()
        self.quests.activate("what_was_sealed")

        # Map state
        self.current_map_id = "hub"
        self.map_data   = ALL_MAPS["hub"]
        self.player_ent = None
        self.enemies    = []
        self.npcs       = []
        self.portals    = []
        self.interacts  = []
        self.killed_enemies = set()   # (map_id, tx, ty)
        self.used_interacts = set()   # (map_id, tx, ty)

        # Camera
        self.cam_x = 0
        self.cam_y = 0

        # Subsystems
        self.dialogue = DialogueManager(self.font_s, self.font_m, SCREEN_W, SCREEN_H)
        self.hud      = HUD(self.font_s, self.font_m, SCREEN_W, SCREEN_H)
        self.inv_ui   = InventoryScreen(self.font_s, self.font_m, SCREEN_W, SCREEN_H)
        self.combat   = CombatManager(self.font_s, self.font_m, self.font_l,
                                      SCREEN_W, SCREEN_H)
        self.floats   = FloatingText()
        self.notify   = NotificationBar(self.font_s, SCREEN_W, SCREEN_H)
        self.bg_surface = None  # screenshot for combat overlay

        # Input throttle
        self.move_timer = 0
        self.MOVE_DELAY = 0.12

        # Menu state
        self.menu_sel   = 0
        self.name_input = ""
        self.name_cursor_blink = 0

    def _init_fonts(self):
        try:
            fonts = [f for f in pygame.font.get_fonts()
                     if "mono" in f or "courier" in f or "consol" in f]
            fname = fonts[0] if fonts else None
            self.font_s = pygame.font.SysFont(fname, 14) if fname else pygame.font.Font(None, 18)
            self.font_m = pygame.font.SysFont(fname, 18) if fname else pygame.font.Font(None, 22)
            self.font_l = pygame.font.SysFont(fname, 28) if fname else pygame.font.Font(None, 34)
        except Exception:
            self.font_s = pygame.font.Font(None, 18)
            self.font_m = pygame.font.Font(None, 22)
            self.font_l = pygame.font.Font(None, 34)

    # ── Map Loading ───────────────────────────────────────────────────────────

    def load_map(self, map_id, target_tx=None, target_ty=None):
        self.current_map_id = map_id
        self.map_data = ALL_MAPS[map_id]
        enemies_raw, npcs_raw, portals_raw, ints_raw = build_entities(self.map_data)

        # Restore kill/use state
        self.enemies   = [e for e in enemies_raw
                          if (map_id, e.tx, e.ty) not in self.killed_enemies]
        self.npcs      = npcs_raw
        self.portals   = portals_raw
        self.interacts = ints_raw
        for i in self.interacts:
            if (map_id, i.tx, i.ty) in self.used_interacts:
                i.used = True
                i.data["opened"] = True

        # Player spawn
        if target_tx is not None and target_ty is not None:
            sx, sy = target_tx, target_ty
        else:
            sx, sy = self.map_data.player_start

        if self.player_ent is None:
            self.player_ent = Player(sx, sy)
        else:
            self.player_ent.tx = sx
            self.player_ent.ty = sy

        self.update_camera()

    def update_camera(self):
        px = self.player_ent.tx * TILE_SIZE + TILE_SIZE // 2
        py = self.player_ent.ty * TILE_SIZE + TILE_SIZE // 2
        self.cam_x = px - SCREEN_W // 2
        self.cam_y = py - SCREEN_H // 2
        map_pw = self.map_data.pixel_width()
        map_ph = self.map_data.pixel_height()
        self.cam_x = max(0, min(self.cam_x, map_pw - SCREEN_W))
        self.cam_y = max(0, min(self.cam_y, map_ph - SCREEN_H))

    # ── Main Loop ─────────────────────────────────────────────────────────────

    def run(self):
        dt = 0
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_event(event)

            self.update(dt)
            self.draw()
            pygame.display.flip()
            dt = self.clock.tick(FPS) / 1000

    # ── Event Handling ────────────────────────────────────────────────────────

    def handle_event(self, event):
        if self.state == ST_MENU:
            self._handle_menu_event(event)
        elif self.state == ST_NAME_INPUT:
            self._handle_name_input_event(event)
        elif self.state == ST_DIALOGUE:
            consumed = self.dialogue.handle_input(event)
            if not consumed:
                pass
        elif self.state == ST_INVENTORY:
            result = self.inv_ui.handle_input(event, self.player)
            if result:
                action, msg = result
                self.notify.push(msg)
            if not self.inv_ui.active:
                self.state = ST_OVERWORLD
        elif self.state == ST_COMBAT:
            if self.combat.active:
                self.combat.handle_input(event)
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.state = ST_OVERWORLD
                if self.combat.state == CS_GAMEOVER if hasattr(CS_GAMEOVER, '__call__') else False:
                    pass
        elif self.state == ST_OVERWORLD:
            self._handle_overworld_event(event)
        elif self.state == ST_GAMEOVER:
            if event.type == pygame.KEYDOWN:
                self._start_new_game(self.player["name"])
        elif self.state == ST_VICTORY:
            if event.type == pygame.KEYDOWN:
                self.state = ST_OVERWORLD

    def _handle_menu_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        options = ["New Game", "Quit"]
        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu_sel = max(0, self.menu_sel - 1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_sel = min(len(options) - 1, self.menu_sel + 1)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            if options[self.menu_sel] == "New Game":
                self.state = ST_NAME_INPUT
                self.name_input = ""
            elif options[self.menu_sel] == "Quit":
                pygame.quit()
                sys.exit()

    def _handle_name_input_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_RETURN and self.name_input.strip():
            self._start_new_game(self.name_input.strip() or "Warden")
        elif event.key == pygame.K_BACKSPACE:
            self.name_input = self.name_input[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.state = ST_MENU
        elif len(self.name_input) < 18 and event.unicode.isprintable():
            self.name_input += event.unicode

    def _handle_overworld_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_i,):
            self.inv_ui.active = True
            self.inv_ui.sel = 0
            self.state = ST_INVENTORY
        elif event.key in (pygame.K_e, pygame.K_RETURN):
            self._try_interact()

    # ── Game Init ─────────────────────────────────────────────────────────────

    def _start_new_game(self, name):
        self.player   = new_player(name)
        self.progress = {
            "district_1_done": False,
            "district_2_done": False,
            "district_3_done": False,
            "final_done": False,
            "broker_contact": None,
            "captain_talked_down": False,
        }
        self.quests         = QuestManager()
        self.quests.activate("what_was_sealed")
        self.killed_enemies = set()
        self.used_interacts = set()
        self.player_ent     = None
        self.load_map("hub")
        self.state = ST_OVERWORLD
        self.notify.push(f"Welcome, {name}. The Undercroft awaits.", duration=3.0)

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt):
        self.name_cursor_blink += dt
        self.notify.update(dt)
        self.floats.update(dt)
        self.dialogue.update(dt)

        if self.state == ST_COMBAT:
            self.combat.update(dt)
            if not self.combat.active:
                if self.combat.state == CS_DEFEAT:
                    self.state = ST_GAMEOVER
            return

        if self.state != ST_OVERWORLD:
            return

        # Movement
        self.move_timer -= dt
        if self.move_timer <= 0:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if   keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx =  1
            elif keys[pygame.K_UP]    or keys[pygame.K_w]: dy = -1
            elif keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy =  1

            if dx != 0 or dy != 0:
                all_blocking = (
                    [e for e in self.enemies if e.alive] +
                    self.npcs
                )
                # Check for portal step-on after move
                moved = self.player_ent.try_move(dx, dy, self.map_data, all_blocking)
                if moved:
                    self.move_timer = self.MOVE_DELAY
                    self.update_camera()
                    self._check_portal_step()
                    self._check_enemy_bump(dx, dy)

    def _check_portal_step(self):
        px, py = self.player_ent.tx, self.player_ent.ty
        for portal in self.portals:
            if portal.tx == px and portal.ty == py:
                pd = portal.portal_data
                req = pd.get("requires")
                if req and not self.progress.get(req):
                    self.notify.push("This district is not yet accessible.")
                    return
                self._transition(pd["target"], pd["ttx"], pd["tty"])
                return

    def _check_enemy_bump(self, dx, dy):
        pass  # enemies are blocking; combat triggered via proximity check below

    def _get_adjacent_enemy(self):
        px, py = self.player_ent.tx, self.player_ent.ty
        fx, fy = self.player_ent.facing
        tx, ty = px + fx, py + fy
        for e in self.enemies:
            if e.alive and e.tx == tx and e.ty == ty:
                return e
        # Also check standing on same tile (shouldn't happen, but safety)
        for e in self.enemies:
            if e.alive and e.tx == px and e.ty == py:
                return e
        return None

    def _try_interact(self):
        # Check adjacent enemy → combat
        enemy = self._get_adjacent_enemy()
        if enemy:
            self._start_combat(enemy)
            return

        # Check NPC
        itx, ity = self.player_ent.get_interact_tile()
        for npc in self.npcs:
            if npc.tx == itx and npc.ty == ity:
                self._talk_to_npc(npc)
                return

        # Check interactable
        for obj in self.interacts:
            if obj.tx == itx and obj.ty == ity:
                if not obj.used:
                    self._use_interactable(obj)
                else:
                    self.notify.push("Nothing more here.")
                return

        # Check portal from facing tile (can also press E on portal)
        for portal in self.portals:
            if portal.tx == itx and portal.ty == ity:
                pd = portal.portal_data
                req = pd.get("requires")
                if req and not self.progress.get(req):
                    self.notify.push("This district is not yet accessible.")
                    return
                self._transition(pd["target"], pd["ttx"], pd["tty"])
                return

    def _talk_to_npc(self, npc):
        key = npc.dialogue_key
        scripts = DIALOGUES.get(key, {})
        # Pick best script variant
        variant = "default"
        if key == "maren":
            if self.progress.get("district_1_done"):
                variant = "after_district_1"
        pages = scripts.get(variant, scripts.get("default", [["..."]])[0:1])
        self.dialogue.start(pages, speaker=npc.name, on_done=self._dialogue_done)
        self.state = ST_DIALOGUE

    def _use_interactable(self, obj):
        itype = obj.itype
        data  = obj.data

        if itype == "notice_board":
            steps = self.quests.active_steps()
            if steps:
                pages = [["ACTIVE QUESTS"]] + [[s] for s in steps]
            else:
                pages = [["No active quests."],
                         ["Speak to Maren for guidance."]]
            self.dialogue.start(pages, speaker="Notice Board",
                                on_done=self._dialogue_done)
            self.state = ST_DIALOGUE

        elif itype == "chest":
            item = data.get("item")
            obj.used = True
            obj.data["opened"] = True
            self.used_interacts.add((self.current_map_id, obj.tx, obj.ty))
            if item:
                added = add_to_inventory(self.player, item)
                msg = f"Found {item['name']}!" if added else f"{item['name']} — inventory full."
                self.dialogue.start([["You open the chest.", msg]],
                                    on_done=self._dialogue_done)
            else:
                self.dialogue.start([["The chest is empty."]],
                                    on_done=self._dialogue_done)
            self.state = ST_DIALOGUE

        elif itype in ("tunnel", "dead_warden"):
            qid  = data.get("quest")
            step = data.get("step")
            text = data.get("text", ["..."])
            if qid and step:
                self.quests.complete_step(qid, step)
            obj.used = True
            obj.data["opened"] = True
            self.used_interacts.add((self.current_map_id, obj.tx, obj.ty))
            gives = data.get("gives_item")
            if gives:
                added = add_to_inventory(self.player, gives)
                if not added:
                    self.notify.push("Inventory full — item left behind.")
            pages = [line.split("\n") if "\n" in line else [line] for line in text]
            pages_flat = [[t] for t in text]
            self.dialogue.start(pages_flat, on_done=self._dialogue_done)
            self.state = ST_DIALOGUE

    def _dialogue_done(self):
        self.state = ST_OVERWORLD

    def _start_combat(self, enemy_sprite):
        self.bg_surface = self.screen.copy()
        self.state = ST_COMBAT

        def on_victory(enemy_name, drops, leveled):
            enemy_sprite.alive = False
            self.killed_enemies.add((self.current_map_id,
                                     enemy_sprite.tx, enemy_sprite.ty))
            # Give drops
            for drop_name in drops:
                for si in STORY_ITEMS:
                    if si["name"] == drop_name:
                        add_to_inventory(self.player, si)
                        self.notify.push(f"Obtained: {drop_name}")
            if leveled:
                self.notify.push(f"Level up! Now Lv.{self.player['level']}", duration=3.0)
            # Quest progress
            if enemy_name == "The First Crack":
                self.quests.complete_step("what_was_sealed", "defeat_boss")
                self.quests.complete_quest("what_was_sealed")
                self.progress["district_1_done"] = True
                self.player.setdefault("ability_cooldowns", {})
                self.notify.push("District 1 cleared! Ability unlocked: War Cry", duration=4.0)
            elif enemy_name == "The Broker":
                self.quests.complete_step("the_orders_debt", "defeat_broker")
                self.quests.complete_quest("the_orders_debt")
                self.progress["district_2_done"] = True
                self.notify.push("District 2 cleared! Ability unlocked: Last Stand", duration=4.0)
            elif enemy_name == "The Last Captain":
                self.quests.complete_step("the_last_order", "confront")
                self.quests.complete_quest("the_last_order")
                self.progress["district_3_done"] = True
                self.notify.push("District 3 cleared! Ability unlocked: Warden's Oath", duration=4.0)

        def on_defeat():
            self.state = ST_GAMEOVER

        def on_fled():
            self.state = ST_OVERWORLD

        self.combat.start(self.player, enemy_sprite.data, self.progress,
                          on_victory=on_victory, on_defeat=on_defeat,
                          on_fled=on_fled)

    def _transition(self, target_map, ttx, tty):
        self.notify.push(f"Entering: {target_map.replace('_', ' ').title()}")
        self.load_map(target_map, ttx, tty)

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self):
        if self.state == ST_MENU:
            self._draw_menu()
            return
        if self.state == ST_NAME_INPUT:
            self._draw_name_input()
            return
        if self.state == ST_GAMEOVER:
            self._draw_gameover()
            return

        # Overworld base
        self._draw_overworld()

        if self.state == ST_COMBAT:
            if self.bg_surface:
                self.combat.draw(self.screen, self.bg_surface)
            else:
                self.combat.draw(self.screen, self.screen.copy())
            if not self.combat.active:
                draw_text(self.screen, "Press ENTER to continue",
                          SCREEN_W // 2 - 100, SCREEN_H // 2 + 60,
                          self.font_m, (200, 195, 185))
        elif self.state == ST_DIALOGUE:
            self.dialogue.draw(self.screen)
        elif self.state == ST_INVENTORY:
            self.inv_ui.draw(self.screen, self.player)

        # Always draw HUD and notifications over everything
        if self.state not in (ST_MENU, ST_NAME_INPUT, ST_GAMEOVER, ST_COMBAT):
            self.hud.draw(self.screen, self.player, self.current_map_id, self.quests)

        self.notify.draw(self.screen)

    def _draw_overworld(self):
        palette = self.map_data.palette
        self.screen.fill(palette["bg"])

        # Tiles
        for ty in range(self.map_data.height):
            for tx in range(self.map_data.width):
                tile = self.map_data.tiles[ty][tx]
                x = tx * TILE_SIZE - self.cam_x
                y = ty * TILE_SIZE - self.cam_y
                if x + TILE_SIZE < 0 or x > SCREEN_W or y + TILE_SIZE < 0 or y > SCREEN_H:
                    continue
                color = palette.get(tile, (50, 50, 50))
                pygame.draw.rect(self.screen, color, (x, y, TILE_SIZE, TILE_SIZE))
                # Grid lines (subtle)
                pygame.draw.rect(self.screen, (
                    max(0, color[0] - 8),
                    max(0, color[1] - 8),
                    max(0, color[2] - 8)
                ), (x, y, TILE_SIZE, TILE_SIZE), 1)

        # Portals
        for p in self.portals:
            p.draw(self.screen, self.cam_x, self.cam_y)

        # Interactables
        for obj in self.interacts:
            obj.draw(self.screen, self.cam_x, self.cam_y)

        # NPCs
        for npc in self.npcs:
            npc.draw(self.screen, self.cam_x, self.cam_y)
            # Name label
            lbl = self.font_s.render(npc.name, True, (180, 220, 220))
            lx = npc.tx * TILE_SIZE - self.cam_x + TILE_SIZE // 2 - lbl.get_width() // 2
            ly = npc.ty * TILE_SIZE - self.cam_y - 14
            self.screen.blit(lbl, (lx, ly))

        # Enemies
        for e in self.enemies:
            if not e.alive:
                continue
            e.draw(self.screen, self.cam_x, self.cam_y)
            # HP mini-bar
            ex = e.tx * TILE_SIZE - self.cam_x
            ey = e.ty * TILE_SIZE - self.cam_y - 6
            from ui import draw_hp_bar
            draw_hp_bar(self.screen, ex, ey, e.data.get("hp", e.data.get("max_hp", 1)),
                        e.data.get("max_hp", 1), width=TILE_SIZE, height=4)

        # Player
        self.player_ent.draw(self.screen, self.cam_x, self.cam_y)

        # Floating text
        self.floats.draw(self.screen, self.font_s, self.cam_x, self.cam_y)

    def _draw_menu(self):
        self.screen.fill((8, 6, 4))
        title = self.font_l.render("ASHBOURNE", True, (200, 170, 100))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 140))
        subtitle = self.font_s.render("A city built on the grave of something older.",
                                      True, (100, 90, 75))
        self.screen.blit(subtitle, (SCREEN_W // 2 - subtitle.get_width() // 2, 185))

        options = ["New Game", "Quit"]
        for i, opt in enumerate(options):
            col = (220, 195, 120) if i == self.menu_sel else (120, 110, 90)
            prefix = "> " if i == self.menu_sel else "  "
            surf = self.font_m.render(prefix + opt, True, col)
            self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, 260 + i * 36))

        hint = self.font_s.render("W/S: navigate   ENTER: select", True, (60, 55, 48))
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 50))

    def _draw_name_input(self):
        self.screen.fill((8, 6, 4))
        draw_text(self.screen, "Enter your name, Warden.",
                  SCREEN_W // 2 - 130, 180, self.font_m, (200, 180, 130))

        cursor = "_" if int(self.name_cursor_blink * 2) % 2 == 0 else ""
        name_display = self.name_input + cursor
        surf = self.font_l.render(name_display or "_", True, (210, 190, 150))
        self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, 230))

        pygame.draw.line(self.screen, (120, 100, 70),
                         (SCREEN_W // 2 - 120, 268), (SCREEN_W // 2 + 120, 268), 1)

        hint = self.font_s.render("ENTER to confirm   ESC to go back", True, (70, 65, 55))
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 50))

    def _draw_gameover(self):
        self.screen.fill((4, 3, 2))
        msg = self.font_l.render("YOU HAVE FALLEN", True, (180, 50, 50))
        self.screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, SCREEN_H // 2 - 40))
        sub = self.font_m.render("Press any key to try again.", True, (100, 90, 80))
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2 + 20))


if __name__ == "__main__":
    game = Game()
    game.run()
