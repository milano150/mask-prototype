import pygame
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kaali - The Indigo Force")
clock = pygame.time.Clock()

def draw_kaali_bright(surface, x, y):
    # COLORS - Slightly brighter, more saturated "Electric" Blue
    KAALI_BLUE = (30, 60, 180)     # Bright Indigo Blue
    SILVER_BORDER = (200, 200, 210) # Sharp Silver
    BLACK = (10, 10, 20)           # Deep outline
    WHITE = (255, 255, 255)        # Pure White
    BLOOD_RED = (210, 0, 0)        # Bright Crimson Tongue

    # 1. THE CROWN (Silver Border, Indigo Base)
    # Silver Outer Ring (Centered)
    pygame.draw.circle(surface, SILVER_BORDER, (int(x), int(y)), 130, draw_top_left=True, draw_top_right=True)
    # Bright Blue Inner Crown
    pygame.draw.circle(surface, KAALI_BLUE, (int(x), int(y)), 122, draw_top_left=True, draw_top_right=True)
    
    # 2. THE FACE BASE (Indigo)
    face_points = [
        (x - 60, y - 40), (x + 60, y - 40),
        (x + 75, y + 20), (x + 45, y + 100),
        (x, y + 135),
        (x - 45, y + 100), (x - 75, y + 20)
    ]
    pygame.draw.polygon(surface, KAALI_BLUE, face_points)
    pygame.draw.polygon(surface, BLACK, face_points, 4) 

    # 3. THE EYES (Piercing White Pupils)
    pygame.draw.circle(surface, BLACK, (int(x - 28), int(y + 20)), 22)
    pygame.draw.circle(surface, BLACK, (int(x + 28), int(y + 20)), 22)
    pygame.draw.circle(surface, WHITE, (int(x - 28), int(y + 20)), 6)
    pygame.draw.circle(surface, WHITE, (int(x + 28), int(y + 20)), 6)

    # 4. THE THIRD EYE (Vertical)
    pygame.draw.ellipse(surface, WHITE, (x - 7, y - 28, 14, 28))
    pygame.draw.circle(surface, BLOOD_RED, (int(x), int(y - 14)), 4)

    # 5. THE RED TONGUE (Protruding)
    tongue_rect = (x - 14, y + 85, 28, 55)
    pygame.draw.rect(surface, BLOOD_RED, tongue_rect, border_bottom_left_radius=14, border_bottom_right_radius=14)
    # Vertical detail line on tongue
    pygame.draw.line(surface, (120, 0, 0), (x, y + 85), (x, y + 130), 2)

    # 6. FANGS
    pygame.draw.polygon(surface, WHITE, [(x-28, y+80), (x-12, y+80), (x-20, y+102)])
    pygame.draw.polygon(surface, WHITE, [(x+12, y+80), (x+28, y+80), (x+20, y+102)])

# MAIN LOOP
while True:
    screen.fill((20, 20, 30)) # Very dark navy background
    
    center_x, center_y = screen.get_rect().center

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Perfectly Centered Drawing
    # (Subtracting 20 from y to balance the crown height)
    draw_kaali_bright(screen, center_x, center_y - 20)

    pygame.display.flip()
    clock.tick(60)