import pygame
import os

# =====================
# CONSTANTS
# =====================
TILE_SIZE = 48

# =====================
# SPRITE SHEET CLASS
# =====================
class SpriteSheet:
    def __init__(self, filename):
        """Loads the sheet with transparency support."""
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_sprite(self, x, y, w=16, h=16, target_w=TILE_SIZE, target_h=TILE_SIZE):
        """Extracts and scales a sprite from the sheet."""
        rect = pygame.Rect(x, y, w, h)
        image = pygame.Surface((w, h), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        return pygame.transform.scale(image, (int(target_w), int(target_h)))

# =====================
# INTERACTIVE CLASSES
# =====================
class SlidingObject:
    def __init__(self, x, y, sprite, slide_limit=TILE_SIZE, is_locked=False, requires_key=False):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.sprite = sprite
        self.offset_x = 0
        self.is_open = False
        self.max_slide = slide_limit
        # NEW: Lock properties
        self.is_locked = is_locked
        self.requires_key = requires_key

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
    """Initializes assets and parses the map for main.py."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MAP_PATH = os.path.join(BASE_DIR, "map.txt")
    
    with open(MAP_PATH, "r") as f:
        game_map = [list(line.rstrip()) for line in f]

    # --- 1. DEFINE YOUR SHEETS ---
    # To add more sheets, just add: another_sheet = SpriteSheet(os.path.join(BASE_DIR, "new.png"))
    castle_sheet = SpriteSheet(os.path.join(BASE_DIR, "castle.png"))
    cave_sheet   = SpriteSheet(os.path.join(BASE_DIR, "cave.png"))
    
    # --- 2. DEFINE ASSETS ---
    assets = {
        'wall':         castle_sheet.get_sprite(120, 60, 16, 16),
        'wall2':        castle_sheet.get_sprite(107, 235, 32, 18),
        'floor':        cave_sheet.get_sprite(16, 16, 16, 16),
        'window':       castle_sheet.get_sprite(96, 255, 32, 33, TILE_SIZE * 1.5, TILE_SIZE * 2),
        'torch':        castle_sheet.get_sprite(98, 288, 32, 31, TILE_SIZE * 0.8, TILE_SIZE),
        'bucket':       castle_sheet.get_sprite(41, 108, 14, 18, TILE_SIZE * 0.65, TILE_SIZE * 0.75),
        'barrel':       castle_sheet.get_sprite(37, 67, 22, 28, TILE_SIZE * 0.75, TILE_SIZE * 0.85),
        'spearholder':  castle_sheet.get_sprite(32, 210, 62, 78, TILE_SIZE * 1.5, TILE_SIZE),
        'bridge':       castle_sheet.get_sprite(352, 28, 96, 21, TILE_SIZE * 2, TILE_SIZE * 1),
        'door':         castle_sheet.get_sprite(385, 210, 62, 78, TILE_SIZE * 1.5, TILE_SIZE * 2),
        'key':          castle_sheet.get_sprite(144, 112, 16, 16, TILE_SIZE * 0.6, TILE_SIZE * 0.6)
    }

    walls, interactables, items = [], [], []
    spawn = (100, 100)

    # --- 3. PARSE MAP ---
    for r, row in enumerate(game_map):
        for c, char in enumerate(row):
            world_x, world_y = c * TILE_SIZE, r * TILE_SIZE
            
            # --- STATIC SOLIDS (Walls) ---
            if char == "W": # Normal Wall
                walls.append(pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE))
            elif char == "2": # Wall Style 2
                walls.append(pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE))

            # --- INTERACTIVE DOORS ---
            elif char == "D": # Normal Door
                interactables.append(SlidingObject(world_x, world_y, assets['door']))
            elif char == "L": # Level Exit Door (Locked)
                interactables.append(SlidingObject(world_x, world_y, assets['door'], is_exit=True))

            # --- SOLID ITEMS (Barrel & Bucket) ---
            elif char == "A": # Barrel
                items.append({'char': 'A', 'rect': pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)})
            elif char == "B": # Bucket
                items.append({'char': 'B', 'rect': pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)})

            # --- COLLECTIBLES ---
            elif char == "k": # Key
                items.append({'char': 'k', 'rect': pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)})

            # --- PLAYER SPAWN ---
            elif char == "P":
                spawn = (world_x + TILE_SIZE // 2, world_y + TILE_SIZE // 2)

   
    return game_map, walls, interactables, items, spawn, assets