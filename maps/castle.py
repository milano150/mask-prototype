import pygame
import sys
import os
import math

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

    def get_sprite(self, x, y, w=16, h=16, target_w=TILE_SIZE, target_h=TILE_SIZE):
        rect = pygame.Rect(x, y, w, h)
        image = pygame.Surface((w, h), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        return pygame.transform.scale(image, (int(target_w), int(target_h)))

# =====================
# INTERACTIVE CLASSES
# =====================
class SlidingObject:
    """Base class for things that slide sideways (Doors/Grills)"""
    def __init__(self, x, y, sprite, slide_limit=TILE_SIZE):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.sprite = sprite
        self.offset_x = 0
        self.is_open = False
        self.max_slide = slide_limit

    def update(self, dt):
        speed = 200 * dt  # Smooth sliding speed
        if self.is_open and self.offset_x < self.max_slide:
            self.offset_x += speed
        elif not self.is_open and self.offset_x > 0:
            self.offset_x -= speed

    def draw(self, screen, camera):
        # Adjust Y based on sprite height (for tall doors)
        draw_x = self.rect.x - camera[0] + self.offset_x
        draw_y = self.rect.y - camera[1] - (self.sprite.get_height() - TILE_SIZE)
        screen.blit(self.sprite, (draw_x, draw_y))

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
    ui_font = pygame.font.SysFont("Arial", 20, bold=True)

    # -------- ASSETS --------
    castle_sheet = SpriteSheet("castle.png")
    cave_sheet = SpriteSheet("cave.png")

    assets = {
        'wall':   castle_sheet.get_sprite(120, 60),
        'floor':  cave_sheet.get_sprite(16, 16),
        # Centered small bucket
        'bucket': castle_sheet.get_sprite(41, 108, 14, 18, TILE_SIZE*0.7, TILE_SIZE*0.8),
        # Tall sliding door
        'door':   castle_sheet.get_sprite(385, 210, 62, 78, TILE_SIZE*1.3, TILE_SIZE*1.8),
        # Metal grill
        'grill':  castle_sheet.get_sprite(160, 48, 16, 16) 
    }

    # -------- MAP DATA --------
    BASE_DIR = os.path.dirname(__file__)
    MAP_PATH = os.path.join(BASE_DIR, "map.txt")
    game_map = load_map(MAP_PATH)

    walls = []
    buckets = []
    interactables = [] # Doors and Grills
    player = None

    for r, row in enumerate(game_map):
        for c, char in enumerate(row):
            world_x, world_y = c * TILE_SIZE, r * TILE_SIZE

            if char == "W":
                walls.append(pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE))
            elif char == "B":
                buckets.append(pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE))
            elif char == "D":
                interactables.append(SlidingObject(world_x, world_y, assets['door'], TILE_SIZE * 1.2))
            elif char == "G":
                interactables.append(SlidingObject(world_x, world_y, assets['grill']))
            elif char == "P":
                player = Player(world_x + TILE_SIZE // 2, world_y + TILE_SIZE // 2)
                game_map[r][c] = "."

    if player is None: raise RuntimeError("No player spawn (P)")

    # =====================
    # GAME LOOP
    # =====================
    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        interaction_text = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                for obj in interactables:
                    dist = math.hypot(player.rect.centerx - obj.rect.centerx, 
                                      player.rect.centery - obj.rect.centery)
                    if dist < TILE_SIZE * 1.5:
                        obj.is_open = not obj.is_open

        keys = pygame.key.get_pressed()

        # -------- UPDATE --------
        old_rect = player.rect.copy()
        player.update(keys, dt)

        # Collision with Walls, Buckets, and CLOSED interactables
        solid_objs = walls + buckets + [o.rect for o in interactables if not o.is_open]
        for obj in solid_objs:
            if player.rect.colliderect(obj):
                player.rect = old_rect
                break

        for obj in interactables:
            obj.update(dt)
            # Check for interaction prompt
            dist = math.hypot(player.rect.centerx - obj.rect.centerx, 
                              player.rect.centery - obj.rect.centery)
            if dist < TILE_SIZE * 1.5:
                status = "CLOSE" if obj.is_open else "OPEN"
                interaction_text = ui_font.render(f"[E] TO {status}", True, (255, 255, 255))

        # -------- CAMERA --------
        camera_x = player.rect.centerx - SCREEN_W // 2
        camera_y = player.rect.centery - SCREEN_H // 2

        # -------- DRAW --------
        screen.fill((20, 20, 25))

        # 1. Floor & Walls & Buckets
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                draw_x, draw_y = c * TILE_SIZE - camera_x, r * TILE_SIZE - camera_y
                if -TILE_SIZE < draw_x < SCREEN_W and -TILE_SIZE < draw_y < SCREEN_H:
                    screen.blit(assets['floor'], (draw_x, draw_y))
                    if char == "W":
                        screen.blit(assets['wall'], (draw_x, draw_y))
                    elif char == "B":
                        # Center bucket in tile
                        bx = draw_x + (TILE_SIZE - assets['bucket'].get_width()) // 2
                        by = draw_y + (TILE_SIZE - assets['bucket'].get_height()) // 2
                        screen.blit(assets['bucket'], (bx, by))

        # 2. Player (Drawn before doors so character is "behind" arches)
        player.draw(screen, (camera_x, camera_y))

        # 3. Doors & Grills
        for obj in interactables:
            obj.draw(screen, (camera_x, camera_y))

        # 4. UI Prompt
        if interaction_text:
            screen.blit(interaction_text, (SCREEN_W//2 - interaction_text.get_width()//2, SCREEN_H - 100))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()