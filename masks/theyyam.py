import pygame
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 400, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Crimson Guardian - Theyyam Mask")
clock = pygame.time.Clock()

def draw_single_theyyam(surface, x, y):
    # COLORS
    RED = (180, 0, 0)
    BLACK = (15, 15, 15)
    WHITE = (255, 255, 255)
    GOLD = (218, 165, 32)

    # 1. THE LARGE CROWN (Prabhamandala)
    # Drawing layers of the semi-circle halo
    pygame.draw.circle(surface, GOLD, (x, y + 20), 120, draw_top_left=True, draw_top_right=True)
    pygame.draw.circle(surface, RED, (x, y + 20), 110, draw_top_left=True, draw_top_right=True)
    
    # 2. THE FACE BASE
    face_points = [
        (x - 60, y - 40), (x + 60, y - 40), # Top
        (x + 70, y + 20), (x + 40, y + 100), # Right side
        (x, y + 130),                        # Chin
        (x - 40, y + 100), (x - 70, y + 20)  # Left side
    ]
    pygame.draw.polygon(surface, RED, face_points)
    pygame.draw.polygon(surface, BLACK, face_points, 3) 

    # 3. THE INTENSE EYES
    pygame.draw.circle(surface, BLACK, (x - 25, y + 20), 18)
    pygame.draw.circle(surface, BLACK, (x + 25, y + 20), 18)
    pygame.draw.circle(surface, WHITE, (x - 25, y + 20), 5)
    pygame.draw.circle(surface, WHITE, (x + 25, y + 20), 5)

    # 4. THE ICONIC MUSTACHE
    pygame.draw.arc(surface, BLACK, (x - 55, y + 60, 60, 40), 3.14, 0, 8)
    pygame.draw.arc(surface, BLACK, (x - 5, y + 60, 60, 40), 3.14, 0, 8)

    # 5. RITUAL MARKINGS (Pookkutty)
    for i in range(-50, 51, 15):
        pygame.draw.circle(surface, WHITE, (x + i, y - 10), 3) 
    for i in range(-30, 31, 10):
        pygame.draw.circle(surface, WHITE, (x + i, y + 115), 2)

# MAIN LOOP
while True:
    screen.fill((25, 25, 25)) 
    
    # Get the center of the screen dynamically
    center_x, center_y = screen.get_rect().center

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Drawing at center_y - 20 to balance the weight of the chin and crown
    draw_single_theyyam(screen, center_x, center_y - 20)

    pygame.display.flip()
    clock.tick(60)