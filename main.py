import pygame
import sys
from player import Player

# Initialize pygame
pygame.init()

# Create window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mask Game")

clock = pygame.time.Clock()
FPS = 60
player = Player(WIDTH // 2, HEIGHT // 2)

# Main loop
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill screen with a color
    screen.fill((30, 30, 30))

    keys = pygame.key.get_pressed()
    player.update(keys)
    player.draw(screen)

    # Update display
    pygame.display.flip()

# Cleanup
pygame.quit()
sys.exit()