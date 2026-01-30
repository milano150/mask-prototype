import pygame
import math
import sys

# --- Configuration ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
GHOST_SPEED = 3

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLOR = (0, 200, 255)  # Cyan
GHOST_COLOR = (255, 50, 50)   # Red

def run_simulation():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Top-Down Ghost Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 36)

    # Initialize Positions
    player_rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 30, 30)
    ghost_rect = pygame.Rect(100, 100, 30, 30)
    
    game_over = False

    while True:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not game_over:
            # 2. Player Movement (Windows Keyboard Input)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: player_rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_rect.x += PLAYER_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]: player_rect.y -= PLAYER_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: player_rect.y += PLAYER_SPEED

            # Keep player on screen
            player_rect.clamp_ip(screen.get_rect())

            # 3. Ghost AI Logic (Chase)
            dx = player_rect.centerx - ghost_rect.centerx
            dy = player_rect.centery - ghost_rect.centery
            distance = math.hypot(dx, dy)

            if distance != 0:
                # Move ghost towards player
                ghost_rect.x += (dx / distance) * GHOST_SPEED
                ghost_rect.y += (dy / distance) * GHOST_SPEED

            # 4. Collision Check (The Attack)
            if ghost_rect.colliderect(player_rect):
                game_over = True

        # 5. Drawing
        screen.fill(BLACK) # Background
        
        pygame.draw.rect(screen, PLAYER_COLOR, player_rect, border_radius=5)
        pygame.draw.rect(screen, GHOST_COLOR, ghost_rect, border_radius=15) # Ghost is rounder

        if game_over:
            text = font.render("CAUGHT BY GHOST! Press ESC to Exit", True, WHITE)
            screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    run_simulation()