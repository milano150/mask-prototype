import pygame
import sys
import os
import math

# --- PATH LOGIC ---
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
def get_path(filename):
    return os.path.join(BASE_PATH, filename)

# --- CONFIGURATION ---
TILE_SIZE = 64 
SCREEN_W, SCREEN_H = 1024, 768
FPS = 60

class SpriteSheet:
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except Exception as e:
            print(f"Error: {e}")
            pygame.quit()
            sys.exit()
        
    def get_sprite(self, x, y, w, h, target_w, target_h=None):
        if target_h is None: target_h = target_w
        rect = pygame.Rect(x, y, w, h)
        image = pygame.Surface((w, h), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        return pygame.transform.scale(image, (int(target_w), int(target_h)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Castle Explorer - Sideways Door")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20, bold=True)

    # Assets
    castle_sheet = SpriteSheet(get_path("castle.png"))
    cave_sheet = SpriteSheet(get_path("cave.png"))
    
    tiles = {
        'wall':   castle_sheet.get_sprite(120, 60, 16, 16, TILE_SIZE),
        'floor':  cave_sheet.get_sprite(16, 16, 16, 16, TILE_SIZE),
        'bucket': castle_sheet.get_sprite(41, 108, 14, 18, TILE_SIZE * 0.75, TILE_SIZE * 0.9),
        'door':   castle_sheet.get_sprite(385, 210, 62, 78, TILE_SIZE * 1.5, TILE_SIZE * 2),
    }

    # Load Map
    # NOTE: In your map.txt, place a 'W' above the 'D' to stop the player from walking into the arch.
    with open(get_path("map.txt"), "r") as f:
        game_map = [list(line.strip('\n')) for line in f.readlines()]

    player_size = 32
    player_x, player_y = 0, 0
    door_state = "closed" 
    door_x_offset = 0.0   # Horizontal offset for sideways sliding
    max_slide = TILE_SIZE * 1.1 # How far sideways it moves
    
    for r, row in enumerate(game_map):
        for c, char in enumerate(row):
            if char == "P":
                player_x, player_y = c * TILE_SIZE + 16, r * TILE_SIZE + 16

    player_speed = 5

    while True:
        clock.tick(FPS)
        show_prompt = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                for r, row in enumerate(game_map):
                    for c, char in enumerate(row):
                        if char == "D":
                            dist = math.hypot(player_x - (c * TILE_SIZE), player_y - (r * TILE_SIZE))
                            if dist < TILE_SIZE * 2.5:
                                if door_state == "closed": door_state = "opening"
                                elif door_state == "open": door_state = "closing"

        # Sideways Animation Logic
        if door_state == "opening":
            door_x_offset += 5
            if door_x_offset >= max_slide:
                door_x_offset = max_slide
                door_state = "open"
        elif door_state == "closing":
            door_x_offset -= 5
            if door_x_offset <= 0:
                door_x_offset = 0
                door_state = "closed"

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -player_speed
        if keys[pygame.K_s]: dy = player_speed
        if keys[pygame.K_a]: dx = -player_speed
        if keys[pygame.K_d]: dx = player_speed

        # Collision
        is_solid = door_state != "open"
        solid_chars = "WD" if is_solid else "W"
        
        player_x += dx
        p_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                if c < len(row) and char in solid_chars:
                    tr = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if p_rect.colliderect(tr):
                        if dx > 0: player_x = tr.left - player_size
                        if dx < 0: player_x = tr.right

        player_y += dy
        p_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                if c < len(row) and char in solid_chars:
                    tr = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if p_rect.colliderect(tr):
                        if dy > 0: player_y = tr.top - player_size
                        if dy < 0: player_y = tr.bottom

        cam_x = player_x - (SCREEN_W // 2) + (player_size // 2)
        cam_y = player_y - (SCREEN_H // 2) + (player_size // 2)

        screen.fill((20, 20, 25))

        # 1. Floor
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                if char != " ":
                    screen.blit(tiles['floor'], (c*TILE_SIZE-cam_x, r*TILE_SIZE-cam_y))

        # 2. Objects
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                draw_x, draw_y = c*TILE_SIZE-cam_x, r*TILE_SIZE-cam_y
                if char == "W":
                    screen.blit(tiles['wall'], (draw_x, draw_y))
                elif char == "B":
                    b_img = tiles['bucket']
                    screen.blit(b_img, (draw_x + (TILE_SIZE-b_img.get_width())//2, draw_y + (TILE_SIZE-b_img.get_height())//2))
                elif char == "D":
                    dist = math.hypot(player_x - (c * TILE_SIZE), player_y - (r * TILE_SIZE))
                    if dist < TILE_SIZE * 2: show_prompt = True

        # 3. Player
        pygame.draw.rect(screen, (0, 180, 255), (SCREEN_W//2 - 16, SCREEN_H//2 - 16, player_size, player_size))

        # 4. Sliding Door
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                if char == "D":
                    draw_x, draw_y = c*TILE_SIZE-cam_x, r*TILE_SIZE-cam_y
                    d_img = tiles['door']
                    # Apply horizontal slide instead of vertical
                    final_x = draw_x + (TILE_SIZE - d_img.get_width())//2 + door_x_offset
                    final_y = draw_y - (d_img.get_height() - TILE_SIZE)
                    screen.blit(d_img, (final_x, final_y))

        if show_prompt:
            label = "E to CLOSE" if door_state == "open" else "E to OPEN"
            txt = font.render(f"PRESS {label}", True, (255, 255, 255))
            screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, SCREEN_H - 60))

        pygame.display.flip()

if __name__ == "__main__":
    main()