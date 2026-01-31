import pygame
import sys
import os

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
        
    def get_sprite(self, x, y, w, h, target_size):
        rect = pygame.Rect(x, y, w, h)
        image = pygame.Surface((w, h), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        aspect_ratio = w / h
        return pygame.transform.scale(image, (int(target_size * aspect_ratio), int(target_size)))

def create_glow_circle(radius, color):
    """Generates a soft radial glow for light sources"""
    glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -4):
        alpha = int(100 * (1 - r / radius))
        pygame.draw.circle(glow_surf, (*color, alpha), (radius, radius), r)
    return glow_surf

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Castle Explorer - Two Room Map")
    clock = pygame.time.Clock()

    castle = SpriteSheet(get_path("castle.png"))
    cave = SpriteSheet(get_path("cave.png"))

    # Asset Mapping with Correct Coordinates
    tiles = {
        'wall':   castle.get_sprite(120, 60, 16, 16, TILE_SIZE),
        'floor':  cave.get_sprite(16, 16, 16, 16, TILE_SIZE),
        'ent':    castle.get_sprite(420, 240, 48, 64, TILE_SIZE),
        'closed': castle.get_sprite(340, 240, 48, 64, TILE_SIZE),
        'torch':  castle.get_sprite(156, 735, 16, 32, TILE_SIZE),
        'win':    castle.get_sprite(408, 555, 32, 32, TILE_SIZE),
        'barr':   castle.get_sprite(60, 305, 16, 16, TILE_SIZE)
    }

    glow_img = create_glow_circle(90, (255, 160, 60))

    with open(get_path("map.txt"), "r") as f:
        game_map = [line.strip() for line in f.readlines()]

    # Find spawn point at 'P'
    player_world_x, player_world_y = 0, 0
    for r, row in enumerate(game_map):
        for c, char in enumerate(row):
            if char == "P":
                player_world_x, player_world_y = c * TILE_SIZE, r * TILE_SIZE

    player_speed = 5

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Movement and Collision
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -player_speed
        if keys[pygame.K_s]: dy = player_speed
        if keys[pygame.K_a]: dx = -player_speed
        if keys[pygame.K_d]: dx = player_speed

        new_x, new_y = player_world_x + dx, player_world_y + dy
        p_hitbox = pygame.Rect(new_x + 15, new_y + 15, 34, 34)
        
        can_move = True
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                if char in "WBO":
                    if p_hitbox.colliderect(pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)):
                        can_move = False
        if can_move: player_world_x, player_world_y = new_x, new_y

        # Camera centering
        cam_x = player_world_x - (SCREEN_W // 2)
        cam_y = player_world_y - (SCREEN_H // 2)

        screen.fill((20, 20, 25))

        # Render Tiles
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                draw_x = (c * TILE_SIZE) - cam_x
                draw_y = (r * TILE_SIZE) - cam_y

                if -TILE_SIZE < draw_x < SCREEN_W and -TILE_SIZE < draw_y < SCREEN_H:
                    screen.blit(tiles['floor'], (draw_x, draw_y))
                    
                    if char == "W": 
                        screen.blit(tiles['wall'], (draw_x, draw_y))
                    elif char == "P":
                        img = tiles['ent']
                        screen.blit(img, (draw_x + (TILE_SIZE - img.get_width())//2, draw_y - 10))
                    elif char == "O":
                        img = tiles['closed']
                        screen.blit(img, (draw_x + (TILE_SIZE - img.get_width())//2, draw_y - 10))
                    elif char == "T":
                        t_img = tiles['torch']
                        tx = draw_x + (TILE_SIZE - t_img.get_width())//2
                        screen.blit(t_img, (tx, draw_y))
                        # Center circular glow on torch
                        screen.blit(glow_img, (tx + (t_img.get_width()//2) - 90, draw_y + 10 - 90), special_flags=pygame.BLEND_ADD)
                    elif char == "G":
                        g_img = tiles['win']
                        screen.blit(g_img, (draw_x + (TILE_SIZE - g_img.get_width())//2, draw_y))
                    elif char == "B":
                        screen.blit(tiles['barr'], (draw_x, draw_y))

        # Draw Player
        pygame.draw.rect(screen, (0, 150, 255), (SCREEN_W//2, SCREEN_H//2, 32, 32))
        pygame.draw.rect(screen, (255, 255, 255), (SCREEN_W//2, SCREEN_H//2, 32, 32), 2)

        pygame.display.flip()

if __name__ == "__main__":
    main()