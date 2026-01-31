import pygame
import sys
import os

from player import Player

# =====================
# CONSTANTS
# =====================
TILE_SIZE = 48
SCREEN_W, SCREEN_H = 800, 600
FPS = 60


# =====================
# SPRITE SHEET
# =====================
class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_sprite(self, x, y, w=16, h=16):
        rect = pygame.Rect(x, y, w, h)
        image = pygame.Surface((w, h), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        return pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))


# =====================
# MAP LOADER
# =====================
def load_map(filename):
    with open(filename, "r") as f:
        return [list(line.rstrip()) for line in f]


# =====================
# MAIN
# =====================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Castle Map")
    clock = pygame.time.Clock()

    # -------- ASSETS --------
    castle_sheet = SpriteSheet("castle.png")
    cave_sheet = SpriteSheet("cave.png")

    wall_tile = castle_sheet.get_sprite(120, 60)
    floor_tile = cave_sheet.get_sprite(16, 16)

    # -------- MAP --------
    BASE_DIR = os.path.dirname(__file__)
    MAP_PATH = os.path.join(BASE_DIR, "map.txt")

    game_map = load_map(MAP_PATH)


    walls = []
    player = None

    for r, row in enumerate(game_map):
        for c, char in enumerate(row):
            world_x = c * TILE_SIZE
            world_y = r * TILE_SIZE

            if char == "W":
                walls.append(
                    pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)
                )

            elif char == "P":
                # Spawn real Player
                player = Player(
                    world_x + TILE_SIZE // 2,
                    world_y + TILE_SIZE // 2
                )
                game_map[r][c] = "."

    if player is None:
        raise RuntimeError("Map has no player spawn (P)")

    # =====================
    # GAME LOOP
    # =====================
    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # -------- PLAYER UPDATE --------
        old_rect = player.rect.copy()
        player.update(keys, dt)

        # -------- COLLISION (simple & safe) --------
        for wall in walls:
            if player.rect.colliderect(wall):
                player.rect = old_rect
                break

        # -------- CAMERA --------
        camera_x = player.rect.centerx - SCREEN_W // 2
        camera_y = player.rect.centery - SCREEN_H // 2

        # -------- DRAW --------
        screen.fill((20, 20, 25))

        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                draw_x = c * TILE_SIZE - camera_x
                draw_y = r * TILE_SIZE - camera_y

                # simple culling
                if (
                    draw_x < -TILE_SIZE or draw_x > SCREEN_W or
                    draw_y < -TILE_SIZE or draw_y > SCREEN_H
                ):
                    continue

                screen.blit(floor_tile, (draw_x, draw_y))

                if char == "W":
                    screen.blit(wall_tile, (draw_x, draw_y))

        # -------- DRAW PLAYER --------
        player.draw(screen, (camera_x, camera_y))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def load_castle():
    BASE_DIR = os.path.dirname(__file__)
    MAP_PATH = os.path.join(BASE_DIR, "map.txt")

    game_map = load_map(MAP_PATH)
    print("Loading map from:", MAP_PATH)



    walls = []
    spawn = None

    for r, row in enumerate(game_map):
        for c, char in enumerate(row):
            world_x = c * TILE_SIZE
            world_y = r * TILE_SIZE

            if char == "W":
                walls.append(
                    pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)
                )

            elif char == "P":
                spawn = (
                    world_x + TILE_SIZE // 2,
                    world_y + TILE_SIZE // 2
                )
                game_map[r][c] = "."

    return game_map, walls, spawn
