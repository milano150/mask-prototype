import pygame
import sys
from player import Player
import math


# Initialize pygame
pygame.init()

# Create window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mask Game")

# --- MASK UI SETUP ---
mask_icons = {
    "theyyam": pygame.image.load("assets/theyyam.png").convert_alpha(),
    "bhairava": pygame.image.load("assets/bhairava.png").convert_alpha(),
    "kali": pygame.image.load("assets/kali.png").convert_alpha(),
}

wheel_image = pygame.image.load("assets/wheel2.png").convert_alpha()
wheel_image.set_alpha(90)  # 👈 lower = more transparent (try 60–120)

WHEEL_UI_SIZE = 380
wheel_image = pygame.transform.scale(wheel_image, (WHEEL_UI_SIZE, WHEEL_UI_SIZE))


ICON_SIZE = 130
CENTER_SIZE = 180
BOTTOM_Y = HEIGHT - 20
SPACING = 300

wheel_offset = 0.0        
wheel_target = 0.0 

WHEEL_RADIUS = 150     # how curved the wheel is
WHEEL_ARC = math.pi / 4  # total arc (60 degrees)


mask_order = ["theyyam", "bhairava", "kali"]



clock = pygame.time.Clock()
FPS = 60
player = Player(WIDTH // 2, HEIGHT // 2)

# Main loop
running = True
while running:
    dt = clock.tick(FPS) / 1000  
    wheel_offset += (wheel_target - wheel_offset) * 8 * dt


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                player.change_mask("theyyam")
                wheel_target = mask_order.index(player.current_mask)

            if event.key == pygame.K_2:
                player.change_mask("bhairava")
                wheel_target = mask_order.index(player.current_mask)

            if event.key == pygame.K_3:
                player.change_mask("kali")
                wheel_target = mask_order.index(player.current_mask)
            if event.key == pygame.K_SPACE:
                player.shoot_fireball()


    # Fill screen with a color
    screen.fill((30, 30, 30))

    keys = pygame.key.get_pressed()
    player.update(keys, dt)
    player.draw(screen)

    # --- DRAW MASK WHEEL UI ---
    center_x = WIDTH // 2
    center_y = BOTTOM_Y

    VISIBLE_RANGE = 2.2   # how far masks exist
    FADE_RANGE = 0.5      # fade-out distance at edges

    wheel_rect = wheel_image.get_rect(midbottom=(WIDTH // 2, HEIGHT))
    screen.blit(wheel_image, wheel_rect)
    


    for i, mask_name in enumerate(mask_order):
        # position relative to selected mask
        relative_pos = i - wheel_offset


        # map relative position to angle
        angle = relative_pos * WHEEL_ARC

        # curved position
        x = center_x + math.sin(angle) * WHEEL_RADIUS
        y = center_y - math.cos(angle) * (WHEEL_RADIUS * 0.4)

        # --- DEPTH / FADE FACTOR ---
        distance = abs(relative_pos)

        # Smooth visibility fade
        fade = 1.0
        if distance > VISIBLE_RANGE - FADE_RANGE:
            fade = max(
                0,
                1 - (distance - (VISIBLE_RANGE - FADE_RANGE)) / FADE_RANGE
            )


        # t = 1 at center, 0 at edge
        t = max(0, 1 - distance) ** 2

        # --- SIZE ---
        size = int(ICON_SIZE + (CENTER_SIZE - ICON_SIZE) * t)
        icon = pygame.transform.scale(mask_icons[mask_name], (size, size))

        # --- ROTATION ---
        rotation = -math.degrees(angle) * 0.8
        icon = pygame.transform.rotate(icon, rotation)

        # --- OPACITY (FADE OUT) ---
        alpha = int((80 + 175 * t) * fade)
        icon.set_alpha(alpha)


        rect = icon.get_rect(center=(x, y))
        screen.blit(icon, rect)





    pygame.display.flip()

# Cleanup
pygame.quit()
sys.exit()