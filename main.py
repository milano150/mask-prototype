import pygame
import sys
from player import Player, BAR_WIDTH, BAR_HEIGHT
import math

# Initialize pygame
pygame.init()

font = pygame.font.Font("assets/fonts/MinecraftRegular-Bmg3.otf", 25)

# Create window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mask Game")

health_bar_img = pygame.image.load("assets/healthbar.png").convert_alpha()

# --- MASK UI SETUP ---
mask_icons = {
    "theyyam": pygame.image.load("assets/theyyam.png").convert_alpha(),
    "bhairava": pygame.image.load("assets/bhairava.png").convert_alpha(),
    "kali": pygame.image.load("assets/kali.png").convert_alpha(),
}

wheel_image = pygame.image.load("assets/wheel2.png").convert_alpha()
wheel_image.set_alpha(90)

WHEEL_UI_SIZE = 300
wheel_image = pygame.transform.scale(wheel_image, (WHEEL_UI_SIZE, WHEEL_UI_SIZE))

# UI constants
ICON_SIZE = 80
CENTER_SIZE = 100
BOTTOM_Y = HEIGHT - 10

BAR_VISIBLE_Y = int(BAR_HEIGHT * 0.4)
BAR_VISIBLE_H = int(BAR_HEIGHT * 0.25)

wheel_offset = 0.0
wheel_target = 0.0

mask_name_timer = 0.0
MASK_NAME_DURATION = 1.0
MASK_NAME_FADE = 0.5

WHEEL_RADIUS = 120
WHEEL_ARC = math.pi / 4

mask_order = ["theyyam", "bhairava", "kali"]

clock = pygame.time.Clock()
FPS = 60

player = Player(WIDTH // 2, HEIGHT // 2)

# Main loop
running = True
while running:
    dt = clock.tick(FPS) / 1000
    wheel_offset += (wheel_target - wheel_offset) * 8 * dt

    if mask_name_timer > 0:
        mask_name_timer -= dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                player.change_mask("theyyam")
                wheel_target = mask_order.index(player.current_mask)
                mask_name_timer = MASK_NAME_DURATION + MASK_NAME_FADE

            if event.key == pygame.K_2:
                player.change_mask("bhairava")
                wheel_target = mask_order.index(player.current_mask)
                mask_name_timer = MASK_NAME_DURATION + MASK_NAME_FADE

            if event.key == pygame.K_3:
                player.change_mask("kali")
                wheel_target = mask_order.index(player.current_mask)
                mask_name_timer = MASK_NAME_DURATION + MASK_NAME_FADE

            if event.key == pygame.K_SPACE:
                player.shoot_fireball()

            if event.key == pygame.K_h:
                player.take_damage(10)

            if event.key == pygame.K_SPACE:
                if player.current_mask == "kali" and not player.sword_swinging:
                    player.sword_swinging = True
                    player.sword_timer = player.sword_duration
                    player.sword_angle = 90 if player.facing == 1 else -105

    keys = pygame.key.get_pressed()
    player.update(keys, dt)

    screen.fill((20, 20, 20))

    player.draw(screen)

    # --- HEALTH BAR ---
    bar_rect = player.health_bar.get_frame_rect()

    cropped_rect = pygame.Rect(
        bar_rect.x,
        bar_rect.y + BAR_VISIBLE_Y,
        BAR_WIDTH,
        BAR_VISIBLE_H
    )

    frame = pygame.Surface((BAR_WIDTH, BAR_VISIBLE_H), pygame.SRCALPHA)
    frame.blit(health_bar_img, (0, 0), cropped_rect)

    UI_WIDTH, UI_HEIGHT = 260, 70
    frame = pygame.transform.scale(frame, (UI_WIDTH, UI_HEIGHT))

    x = (WIDTH - UI_WIDTH) // 2
    y = 4
    screen.blit(frame, (x, y))

    # --- MASK WHEEL ---
    wheel_rect = wheel_image.get_rect(midbottom=(WIDTH // 2, HEIGHT))
    screen.blit(wheel_image, wheel_rect)

    if mask_name_timer > 0:
        mask_name = player.current_mask
        alpha = 255 if mask_name_timer > MASK_NAME_FADE else int(
            255 * (mask_name_timer / MASK_NAME_FADE)
        )

        text_surface = font.render(mask_name, True, (230, 230, 230))
        text_surface.set_alpha(alpha)

        text_rect = text_surface.get_rect(
            midbottom=(wheel_rect.centerx, wheel_rect.top + 200)
        )
        screen.blit(text_surface, text_rect)

    center_x = WIDTH // 2
    center_y = BOTTOM_Y

    for i, name in enumerate(mask_order):
        relative_pos = i - wheel_offset
        if abs(relative_pos) > 1.5:
            continue

        angle = relative_pos * WHEEL_ARC
        x = center_x + math.sin(angle) * WHEEL_RADIUS
        y = center_y - math.cos(angle) * (WHEEL_RADIUS * 0.4)

        distance = abs(relative_pos)
        t = max(0, 1 - distance) ** 2

        size = int(ICON_SIZE + (CENTER_SIZE - ICON_SIZE) * t)
        icon = pygame.transform.scale(mask_icons[name], (size, size))

        alpha = int(80 + 175 * t)
        icon.set_alpha(alpha)

        rect = icon.get_rect(center=(x, y))
        screen.blit(icon, rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
