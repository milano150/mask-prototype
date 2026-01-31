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
        
    def get_sprite(self, x, y, w, h, target_w, target_h=None):
        if target_h is None: target_h = target_w
        rect = pygame.Rect(x, y, w, h)
        image = pygame.Surface((w, h), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        # Scales sprites while maintaining specific proportions
        return pygame.transform.scale(image, (int(target_w), int(target_h)))

def create_glow_circle(radius, color):
    """Generates a soft radial glow for lighting"""
    glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -4):
        alpha = int(100 * (1 - r / radius))
        pygame.draw.circle(glow_surf, (*color, alpha), (radius, radius), r)
    return glow_surf

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Castle Explorer - Final Build with Buckets")
    clock = pygame.time.Clock()

    # Load Sheets
    castle_sheet = SpriteSheet(get_path("castle.png"))
    cave_sheet = SpriteSheet(get_path("cave.png"))

    # Mapping based on your provided images and coordinates
    tiles = {
        'wall':   castle_sheet.get_sprite(120, 60, 16, 16, TILE_SIZE),
        'floor':  cave_sheet.get_sprite(16, 16, 16, 16, TILE_SIZE),
        'torch':  castle_sheet.get_sprite(385, 710, 32, 48, TILE_SIZE),
        'door':   castle_sheet.get_sprite(820, 535, 110, 155, TILE_SIZE * 2, TILE_SIZE * 2.5),
        # 'B' for Bucket using coordinates X:80, Y:305
        'bucket': castle_sheet.get_sprite(41, 108, 14, 18, TILE_SIZE * 0.7)
    }

    glow_img = create_glow_circle(100, (255, 180, 50))

    # Load Map
    with open(get_path("map.txt"), "r") as f:
        game_map = [line.strip() for line in f.readlines()]

    # Setup Player Position
    player_size = 32
    player_x, player_y = 0, 0
    for r, row in enumerate(game_map):
        for c, char in enumerate(row):
            if char == "P":
                player_x, player_y = c * TILE_SIZE + 16, r * TILE_SIZE + 16

    player_speed = 5

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Input
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -player_speed
        if keys[pygame.K_s]: dy = player_speed
        if keys[pygame.K_a]: dx = -player_speed
        if keys[pygame.K_d]: dx = player_speed

        # --- COLLISION LOGIC (Separated Axis for Smoothness) ---
        # Move X
        player_x += dx
        p_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                # Walls (W) and Buckets (B) are solid obstacles
                if char in "WB":
                    wall_rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if p_rect.colliderect(wall_rect):
                        if dx > 0: player_x = wall_rect.left - player_size
                        if dx < 0: player_x = wall_rect.right

        # Move Y
        player_y += dy
        p_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                if char in "WB":
                    wall_rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if p_rect.colliderect(wall_rect):
                        if dy > 0: player_y = wall_rect.top - player_size
                        if dy < 0: player_y = wall_rect.bottom

        # Camera centering
        cam_x = player_x - (SCREEN_W // 2) + (player_size // 2)
        cam_y = player_y - (SCREEN_H // 2) + (player_size // 2)

        screen.fill((15, 15, 20))

        # --- RENDERING PASS ---
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                draw_x = (c * TILE_SIZE) - cam_x
                draw_y = (r * TILE_SIZE) - cam_y

                # Draw floor base
                if -TILE_SIZE*3 < draw_x < SCREEN_W + TILE_SIZE and -TILE_SIZE*3 < draw_y < SCREEN_H + TILE_SIZE:
                    screen.blit(tiles['floor'], (draw_x, draw_y))
                    
                    if char == "W": 
                        screen.blit(tiles['wall'], (draw_x, draw_y))
                    elif char == "B":
                        b_img = tiles['bucket']
                        # Centered on the tile
                        screen.blit(b_img, (draw_x + (TILE_SIZE - b_img.get_width())//2, draw_y + (TILE_SIZE - b_img.get_height())//2))
                    elif char == "T":
                        t_img = tiles['torch']
                        tx, ty = draw_x + (TILE_SIZE - t_img.get_width())//2, draw_y
                        screen.blit(t_img, (tx, ty))
                        # Light glow
                        screen.blit(glow_img, (tx + t_img.get_width()//2 - 100, ty + 20 - 100), special_flags=pygame.BLEND_ADD)
                    elif char == "D":
                        d_img = tiles['door']
                        # Aligns the base of the tall door to the tile
                        screen.blit(d_img, (draw_x + (TILE_SIZE - d_img.get_width())//2, draw_y - (d_img.get_height() - TILE_SIZE)))

        # Draw Player
        pygame.draw.rect(screen, (0, 150, 255), (SCREEN_W//2 - 16, SCREEN_H//2 - 16, 32, 32))
        pygame.draw.rect(screen, (255, 255, 255), (SCREEN_W//2 - 16, SCREEN_H//2 - 16, 32, 32), 2)

        pygame.display.flip()

if __name__ == "__main__":
    main()