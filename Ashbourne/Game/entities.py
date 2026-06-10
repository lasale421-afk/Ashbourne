import pygame
from maps import TILE_SIZE, T_WALL
from data.enemies import ENEMIES, BOSSES

PLAYER_COLOR   = (200, 180, 120)
NPC_COLOR      = (100, 180, 200)
ENEMY_COLOR    = (180, 80, 80)
BOSS_COLOR     = (160, 60, 200)
PORTAL_COLOR   = (120, 220, 255)
INTERACT_COLOR = (200, 180, 60)


class Entity:
    def __init__(self, tx, ty, color, size=28):
        self.tx = tx
        self.ty = ty
        self.color = color
        self.size = size
        self.alive = True

    @property
    def px(self):
        return self.tx * TILE_SIZE + (TILE_SIZE - self.size) // 2

    @property
    def py(self):
        return self.ty * TILE_SIZE + (TILE_SIZE - self.size) // 2

    def rect(self):
        return pygame.Rect(self.tx * TILE_SIZE, self.ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def draw(self, surface, cam_x, cam_y):
        if not self.alive:
            return
        pygame.draw.rect(surface, self.color,
                         (self.px - cam_x, self.py - cam_y, self.size, self.size))


class Player(Entity):
    def __init__(self, tx, ty):
        super().__init__(tx, ty, PLAYER_COLOR, size=26)
        self.facing = (0, 1)  # direction vector

    def draw(self, surface, cam_x, cam_y):
        x = self.px - cam_x
        y = self.py - cam_y
        s = self.size
        # Body
        pygame.draw.rect(surface, self.color, (x, y, s, s))
        # Direction indicator
        fx, fy = self.facing
        cx, cy = x + s // 2, y + s // 2
        ex = cx + fx * (s // 2 - 2)
        ey = cy + fy * (s // 2 - 2)
        pygame.draw.line(surface, (255, 255, 200), (cx, cy), (ex, ey), 2)

    def try_move(self, dx, dy, map_data, entities):
        nx = self.tx + dx
        ny = self.ty + dy
        if dx != 0 or dy != 0:
            self.facing = (dx, dy)
        if map_data.is_wall(nx, ny):
            return False
        for e in entities:
            if e.alive and e.tx == nx and e.ty == ny:
                return False
        self.tx = nx
        self.ty = ny
        return True

    def get_interact_tile(self):
        return self.tx + self.facing[0], self.ty + self.facing[1]


class EnemySprite(Entity):
    def __init__(self, tx, ty, enemy_data):
        is_boss = enemy_data.get("is_boss", False) or enemy_data["name"] in BOSSES
        color = enemy_data.get("color", BOSS_COLOR if is_boss else ENEMY_COLOR)
        super().__init__(tx, ty, color, size=26 if not is_boss else 30)
        self.data = dict(enemy_data)
        self.is_boss = is_boss
        self.name = enemy_data["name"]

    def draw(self, surface, cam_x, cam_y):
        if not self.alive:
            return
        x = self.px - cam_x
        y = self.py - cam_y
        s = self.size
        pygame.draw.rect(surface, self.color, (x, y, s, s))
        if self.is_boss:
            inner = 6
            pygame.draw.rect(surface, (255, 255, 255),
                             (x + inner, y + inner, s - inner*2, s - inner*2), 1)


class NPCSprite(Entity):
    def __init__(self, tx, ty, name, dialogue_key):
        super().__init__(tx, ty, NPC_COLOR, size=26)
        self.name = name
        self.dialogue_key = dialogue_key

    def draw(self, surface, cam_x, cam_y):
        x = self.px - cam_x
        y = self.py - cam_y
        s = self.size
        pygame.draw.rect(surface, self.color, (x, y, s, s))
        # Small indicator above
        pygame.draw.rect(surface, (255, 255, 100), (x + s//2 - 2, y - 6, 4, 4))


class PortalSprite(Entity):
    def __init__(self, tx, ty, portal_data):
        super().__init__(tx, ty, PORTAL_COLOR, size=32)
        self.portal_data = portal_data
        self.locked = portal_data.get("requires") is not None

    def draw(self, surface, cam_x, cam_y):
        x = self.tx * TILE_SIZE - cam_x
        y = self.ty * TILE_SIZE - cam_y
        color = (80, 80, 80) if self.locked else PORTAL_COLOR
        pygame.draw.rect(surface, color, (x + 4, y + 4, 24, 24), 2)
        # Arrows
        mid = 16
        pygame.draw.polygon(surface, color, [
            (x + mid, y + 6), (x + mid - 5, y + 14), (x + mid + 5, y + 14)
        ])


class InteractableSprite(Entity):
    def __init__(self, tx, ty, itype, data):
        super().__init__(tx, ty, INTERACT_COLOR, size=20)
        self.itype = itype
        self.data = data
        self.used = data.get("opened", False)

    def draw(self, surface, cam_x, cam_y):
        if self.used and self.itype == "chest":
            color = (80, 80, 60)
        else:
            color = self.color
        x = self.px - cam_x
        y = self.py - cam_y
        s = self.size
        pygame.draw.rect(surface, color, (x, y, s, s))
        if self.itype == "notice_board":
            pygame.draw.line(surface, (180, 140, 60),
                             (x + 2, y + 4), (x + s - 2, y + 4), 2)
            pygame.draw.line(surface, (180, 140, 60),
                             (x + 2, y + 8), (x + s - 2, y + 8), 2)
            pygame.draw.line(surface, (180, 140, 60),
                             (x + 2, y + 12), (x + s - 6, y + 12), 2)
        elif self.itype == "chest":
            pygame.draw.rect(surface, (100, 70, 30), (x, y, s, s), 2)
            if not self.used:
                pygame.draw.line(surface, (200, 160, 60),
                                 (x, y + s//2), (x + s, y + s//2), 1)


def build_entities(map_data):
    enemies = []
    npcs    = []
    portals = []
    interactables = []

    for spawn in map_data.enemy_spawns:
        from data.enemies import get_enemy
        edata = get_enemy(spawn["type"])
        if edata:
            edata["is_boss"] = spawn.get("is_boss", False)
            enemies.append(EnemySprite(spawn["tx"], spawn["ty"], edata))

    for nspawn in map_data.npc_spawns:
        npcs.append(NPCSprite(nspawn["tx"], nspawn["ty"],
                              nspawn["name"], nspawn["dialogue_key"]))

    for p in map_data.portals:
        portals.append(PortalSprite(p["tx"], p["ty"], p))

    for i in map_data.interactables:
        interactables.append(InteractableSprite(i["tx"], i["ty"],
                                                 i["type"], i["data"]))

    return enemies, npcs, portals, interactables
