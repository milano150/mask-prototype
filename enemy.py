import pygame
import math
import sys

# --- Configuration ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
GHOST_SPEED = 2.6

def run_simulation():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Constant Speed Round Ghost")
    clock = pygame.time.Clock()

    player_rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 30, 30)
    
    # Use floats for smooth movement calculation
    ghost_x, ghost_y = 100.0, 100.0
    ghost_rect = pygame.Rect(ghost_x, ghost_y, 30, 30)
    
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not game_over:
            # 1. Player Movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: player_rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_rect.x += PLAYER_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]: player_rect.y -= PLAYER_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: player_rect.y += PLAYER_SPEED
            player_rect.clamp_ip(screen.get_rect())

            # 2. Ghost Movement (Up, Down, Left, Right, and Diagonal)
            # Find the distance from ghost to player center
            dx = player_rect.centerx - ghost_rect.centerx
            dy = player_rect.centery - ghost_rect.centery
            distance = math.hypot(dx, dy)

            if distance > 0:
                # Normalizing the vector ensures movement is constant in ALL directions
                # ghost_x += (dx / distance) * speed
                # ghost_y += (dy / distance) * speed
                ghost_x += (dx / distance) * GHOST_SPEED
                ghost_y += (dy / distance) * GHOST_SPEED

            # Sync position back to the Rect for drawing and collision
            ghost_rect.x = int(ghost_x)
            ghost_rect.y = int(ghost_y)

            # 3. Collision Check
            if ghost_rect.colliderect(player_rect):
                game_over = True

        # --- Drawing ---
        screen.fill((15, 15, 15)) 
        
        # Player (Blue Square)
        pygame.draw.rect(screen, (0, 200, 255), player_rect)
        
        # Ghost (Red Circle)
        pygame.draw.circle(screen, (255, 50, 50), ghost_rect.center, 15)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    run_simulation()
