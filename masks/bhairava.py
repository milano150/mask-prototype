import pygame
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 400, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bhairava - Yellow Mask with Red Silhouette")
clock = pygame.time.Clock()

def draw_bhairava_unified(surface, x, y):
    # COLORS
    YELLOW_BASE = (255, 215, 0)   # Face and Crown color
    BORDER_RED = (200, 0, 0)      # Outer Crown Edge
    BLACK = (10, 10, 10)          # Eyes and Outlines
    WHITE = (255, 255, 255)       # Fangs and Third Eye

    # 1. THE CROWN (Base is yellow, Border is red)
    # The Red Border (Outer Layer)
    pygame.draw.circle(surface, BORDER_RED, (int(x), int(y + 20)), 126, draw_top_left=True, draw_top_right=True)
    # The Crown Base (Matches Face)
    pygame.draw.circle(surface, YELLOW_BASE, (int(x), int(y + 20)), 120, draw_top_left=True, draw_top_right=True)
    
    # 2. THE FACE BASE (Yellow Face)
    face_points = [
        (x - 60, y - 40), (x + 60, y - 40),
        (x + 70, y + 20), (x + 40, y + 100),
        (x, y + 130),
        (x - 40, y + 100), (x - 70, y + 20)
    ]
    pygame.draw.polygon(surface, YELLOW_BASE, face_points)
    pygame.draw.polygon(surface, BLACK, face_points, 3) # Face definition

    # 3. THE FIERCE EYES 
    pygame.draw.circle(surface, BLACK, (int(x - 25), int(y + 20)), 20)
    pygame.draw.circle(surface, BLACK, (int(x + 25), int(y + 20)), 20)
    pygame.draw.circle(surface, WHITE, (int(x - 25), int(y + 20)), 5)
    pygame.draw.circle(surface, WHITE, (int(x + 25), int(y + 20)), 5)

    # 4. THE THIRD EYE 
    pygame.draw.ellipse(surface, WHITE, (x - 8, y - 25, 16, 24))
    pygame.draw.circle(surface, BLACK, (int(x), int(y - 13)), 4)

    # 5. THE FANGS
    pygame.draw.polygon(surface, WHITE, [(x-25, y+80), (x-10, y+80), (x-17, y+105)])
    pygame.draw.polygon(surface, WHITE, [(x+10, y+80), (x+25, y+80), (x+17, y+105)])

    # 6. ICONIC MUSTACHE (Black)
    pygame.draw.arc(surface, BLACK, (x - 55, y + 60, 60, 40), 3.14, 0, 6)
    pygame.draw.arc(surface, BLACK, (x - 5, y + 60, 60, 40), 3.14, 0, 6)

# MAIN LOOP
while True:
    screen.fill((25, 25, 25)) 
    
    center_x, center_y = screen.get_rect().center

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Draw centered
    draw_bhairava_unified(screen, center_x, center_y - 20)

    pygame.display.flip()
    clock.tick(60)