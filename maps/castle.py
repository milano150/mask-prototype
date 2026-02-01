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
    def __init__(self, x, y, sprite, slide_limit=TILE_SIZE):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.sprite = sprite
        self.offset_x = 0
        self.is_open = False
        self.max_slide = slide_limit

    def update(self, dt):
        speed = 200 * dt
        if self.is_open and self.offset_x < self.max_slide:
            self.offset_x += speed
        elif not self.is_open and self.offset_x > 0:
            self.offset_x -= speed

    def draw(self, screen, camera):
        draw_x = self.rect.x - camera[0] + self.offset_x
        draw_y = self.rect.y - camera[1] - (self.sprite.get_height() - TILE_SIZE)
        screen.blit(self.sprite, (draw_x, draw_y))

# =====================
# LOAD CASTLE FUNCTION
# =====================
def load_castle():
    """Initializes assets and parses the map data."""
    BASE_DIR = os.path.dirname(__file__)
    MAP_PATH = os.path.join(BASE_DIR, "map.txt")
    
    with open(MAP_PATH, "r") as f:
        game_map = [list(line.rstrip()) for line in f]

    # Load Tilesheets
    castle_sheet = SpriteSheet(os.path.join(BASE_DIR, "castle.png"))
    cave_sheet = SpriteSheet(os.path.join(BASE_DIR, "cave.png"))
    
    # Sprite Configuration
    assets = {
        'wall':   castle_sheet.get_sprite(192, 64, 16, 16),
        'floor':  cave_sheet.get_sprite(16, 16),
        # Bridge: Spans 2 boxes (TILE_SIZE * 2)
        'bridge': castle_sheet.get_sprite(736, 64, 64, 16, TILE_SIZE * 2, TILE_SIZE * 0.5),
        # Torch: Scaled to 1 full box height
        'torch':  castle_sheet.get_sprite(208, 832, 16, 32, TILE_SIZE * 0.8, TILE_SIZE),
        # Barrel & Bucket: Sized for centering
        'barrel': castle_sheet.get_sprite(80, 304, 16, 20, TILE_SIZE * 0.75, TILE_SIZE * 0.85),
        'bucket': castle_sheet.get_sprite(41, 108, 14, 18, TILE_SIZE * 0.65, TILE_SIZE * 0.75),
        # Sliding Door
        'door':   castle_sheet.get_sprite(800, 608, 64, 80, TILE_SIZE * 1.5, TILE_SIZE * 2)
    }

    walls = []
    items = []
    interactables = []
    spawn = (100, 100)

    for r, row in enumerate(game_map):
        for c, char in enumerate(row):
            world_x, world_y = c * TILE_SIZE, r * TILE_SIZE
            if char == "W":
                walls.append(pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE))
            elif char == "D":
                interactables.append(SlidingObject(world_x, world_y, assets['door'], TILE_SIZE * 1.2))
            elif char in ["B", "K"]: # Barrel or Bucket
                items.append({'char': char, 'rect': pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)})
            elif char == "P":
                spawn = (world_x + TILE_SIZE // 2, world_y + TILE_SIZE // 2)

    return game_map, walls, interactables, items, spawn, assets

# =====================
# MAIN
# =====================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Castle Map")
    clock = pygame.time.Clock()
    ui_font = pygame.font.SysFont("Arial", 20, bold=True)

    # Use the new load_castle function
    game_map, walls, interactables, items, spawn, assets = load_castle()
    player = Player(*spawn)

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

        # Collision logic
        item_rects = [i['rect'] for i in items]
        solid_objs = walls + item_rects + [o.rect for o in interactables if not o.is_open]
        for obj in solid_objs:
            if player.rect.colliderect(obj):
                player.rect = old_rect
                break

        for obj in interactables:
            obj.update(dt)
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

        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                draw_x, draw_y = c * TILE_SIZE - camera_x, r * TILE_SIZE - camera_y
                if -TILE_SIZE*2 < draw_x < SCREEN_W and -TILE_SIZE < draw_y < SCREEN_H:
                    screen.blit(assets['floor'], (draw_x, draw_y))
                    
                    if char == "W":
                        screen.blit(assets['wall'], (draw_x, draw_y))
                    elif char == "X": # 2-box Bridge
                        screen.blit(assets['bridge'], (draw_x, draw_y + TILE_SIZE // 4))
                    elif char == "B": # Centered Barrel
                        img = assets['barrel']
                        bx = draw_x + (TILE_SIZE - img.get_width()) // 2
                        by = draw_y + (TILE_SIZE - img.get_height()) // 2
                        screen.blit(img, (bx, by))
                    elif char == "K": # Centered Bucket
                        img = assets['bucket']
                        bx = draw_x + (TILE_SIZE - img.get_width()) // 2
                        by = draw_y + (TILE_SIZE - img.get_height()) // 2
                        screen.blit(img, (bx, by))
                    elif char == "T": # Large Torch
                        img = assets['torch']
                        tx = draw_x + (TILE_SIZE - img.get_width()) // 2
                        screen.blit(img, (tx, draw_y))

        player.draw(screen, (camera_x, camera_y))
        for obj in interactables:
            obj.draw(screen, (camera_x, camera_y))

        if interaction_text:
            screen.blit(interaction_text, (SCREEN_W//2 - interaction_text.get_width()//2, SCREEN_H - 100))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()