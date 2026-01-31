import pygame
import sys

# --- Constants ---
TILE_SIZE = 48 
SCREEN_W, SCREEN_H = 800, 600
FPS = 60

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()
        
    def get_sprite(self, x, y, w=16, h=16):
        rect = pygame.Rect(x, y, w, h)
        image = pygame.Surface((w, h), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        return pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))

def load_map(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()

    # --- Assets ---
    castle_sheet = SpriteSheet("castle.png")
    cave_sheet = SpriteSheet("cave.png")
    
    wall_tile = castle_sheet.get_sprite(120, 60)
    # Adjusted floor coordinates for the solid brown section in cave.png
    floor_tile = cave_sheet.get_sprite(16, 16) 
    
    game_map = load_map("map.txt")

    # Player Initialization
    player_pos = [0, 0]
    for r, row in enumerate(game_map):
        for c, char in enumerate(row):
            if char == "P":
                player_pos = [c * TILE_SIZE, r * TILE_SIZE]

    player_speed = 5
    player_rect = pygame.Rect(player_pos[0], player_pos[1], 32, 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # WASD Movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -player_speed
        if keys[pygame.K_s]: dy = player_speed
        if keys[pygame.K_a]: dx = -player_speed
        if keys[pygame.K_d]: dx = player_speed

        # --- Camera Calculation ---
        # This offsets everything so the player stays centered
        camera_x = player_rect.centerx - SCREEN_W // 2
        camera_y = player_rect.centery - SCREEN_H // 2

        # --- Collision & Rendering ---
        screen.fill((20, 20, 25))
        walls = []
        
        for r, row in enumerate(game_map):
            for c, char in enumerate(row):
                # Calculate position relative to the Camera
                x = c * TILE_SIZE - camera_x
                y = r * TILE_SIZE - camera_y
                
                # Render only if the tile is on screen (Optimization)
                if -TILE_SIZE < x < SCREEN_W and -TILE_SIZE < y < SCREEN_H:
                    screen.blit(floor_tile, (x, y))
                    if char == "W":
                        screen.blit(wall_tile, (x, y))
                        # Collision uses absolute world coordinates
                        walls.append(pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Collision Check
        future_rect = player_rect.copy()
        future_rect.x += dx
        future_rect.y += dy
        if not any(future_rect.colliderect(w) for w in walls):
            player_rect = future_rect

        # Draw Player at the screen center
        # (Since the camera centers on player, player always draws at screen center)
        draw_pos = (player_rect.x - camera_x, player_rect.y - camera_y)
        pygame.draw.rect(screen, (0, 150, 255), (*draw_pos, 32, 32))
        pygame.draw.rect(screen, (255, 255, 255), (*draw_pos, 32, 32), 2)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()