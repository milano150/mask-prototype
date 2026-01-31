import pygame
import sys
from player import Player, BAR_WIDTH, BAR_HEIGHT
import math
from map_loader import MapLoader





# Initialize pygame
pygame.init()

font = pygame.font.Font("assets/fonts/MinecraftRegular-Bmg3.otf", 25)  
game_map = MapLoader("assets/maps/haunted_castel.tmx")


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
wheel_image.set_alpha(90)  # 👈 lower = more transparent (try 60–120)


WHEEL_UI_SIZE = 300
wheel_image = pygame.transform.scale(wheel_image, (WHEEL_UI_SIZE, WHEEL_UI_SIZE))

#defs

ICON_SIZE = 80
CENTER_SIZE = 100
BOTTOM_Y = HEIGHT - 10
SPACING = 300

BAR_VISIBLE_Y = int(BAR_HEIGHT * 0.4)
BAR_VISIBLE_H = int(BAR_HEIGHT * 0.25)


wheel_offset = 0.0        
wheel_target = 0.0 

mask_name_timer = 0.0
MASK_NAME_DURATION = 1.0     # seconds fully visible
MASK_NAME_FADE = 0.5          # fade-out time (seconds)


WHEEL_RADIUS = 120     # how curved the wheel is
WHEEL_ARC = math.pi / 4  # total arc (60 degrees)


mask_order = ["theyyam", "bhairava", "kali"]



clock = pygame.time.Clock()
FPS = 60
spawn_x, spawn_y = game_map.player_spawn
player = Player(spawn_x, spawn_y)
camera_x = 0
camera_y = 0


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
                player.take_damage(10)  # test key
            if event.key == pygame.K_SPACE:
                if player.current_mask == "kali" and not player.sword_swinging:
                    player.sword_swinging = True
                    player.sword_timer = player.sword_duration
                    if player.facing == 1:
                        player.sword_angle = 90
                    else:  # facing left
                        player.sword_angle = -105



    # Fill screen with a color
    game_map.draw(screen, (camera_x, camera_y))


    keys = pygame.key.get_pressed()
    player.update(keys, dt, game_map.walls)

    for wall in game_map.walls:
        if player.rect.colliderect(wall):
            # Simple pushback
            if player.facing == 1:
                player.rect.right = wall.left
            elif player.facing == -1:
                player.rect.left = wall.right


    player.draw(screen, camera_offset=(camera_x, camera_y))


    #camera
    camera_x = player.rect.centerx - WIDTH // 2
    camera_y = player.rect.centery - HEIGHT // 2

    # Clamp camera to map bounds
    camera_x = max(0, min(camera_x, game_map.map_width - WIDTH))
    camera_y = max(0, min(camera_y, game_map.map_height - HEIGHT))


    # --- DRAW MASK WHEEL UI ---
    center_x = WIDTH // 2
    center_y = BOTTOM_Y

    # get full frame rect
    bar_rect = player.health_bar.get_frame_rect()

    # crop ONLY the visible bar area
    cropped_rect = pygame.Rect(
        bar_rect.x,
        bar_rect.y + BAR_VISIBLE_Y,
        BAR_WIDTH,
        BAR_VISIBLE_H
    )

    # extract cropped area
    frame = pygame.Surface((BAR_WIDTH, BAR_VISIBLE_H), pygame.SRCALPHA)
    frame.blit(health_bar_img, (0, 0), cropped_rect)


    # SCALE UP (tweak these numbers if you want it even bigger)
    UI_WIDTH = 260
    UI_HEIGHT = 70
    frame = pygame.transform.scale(frame, (UI_WIDTH, UI_HEIGHT))

    # center horizontally, small margin from top
    x = (WIDTH - UI_WIDTH) // 2
    y = 4


    # draw the bar
    screen.blit(frame, (x, y))


    wheel_rect = wheel_image.get_rect(midbottom=(WIDTH // 2, HEIGHT))
    screen.blit(wheel_image, wheel_rect)

    # MASK TEXT

    if mask_name_timer > 0:
        mask_name = player.current_mask

        if mask_name_timer > MASK_NAME_FADE:
            alpha = 255
        else:
            alpha = int(255 * (mask_name_timer / MASK_NAME_FADE))

        text_surface = font.render(mask_name, True, (230, 230, 230))
        text_surface.set_alpha(alpha)

        text_rect = text_surface.get_rect(
            midbottom=(wheel_rect.centerx, wheel_rect.top + 200)
        )

        screen.blit(text_surface, text_rect)



    


    for i, mask_name in enumerate(mask_order):
        # position relative to selected mask
        relative_pos = i - wheel_offset

        # clamp visible range (optional but cleaner)
        if abs(relative_pos) > 1.5:
            continue

        # map relative position to angle
        angle = relative_pos * WHEEL_ARC

        # curved position
        x = center_x + math.sin(angle) * WHEEL_RADIUS
        y = center_y - math.cos(angle) * (WHEEL_RADIUS * 0.4)

        # --- DEPTH / FADE FACTOR ---
        distance = abs(relative_pos)

        # t = 1 at center, 0 at edge
        t = max(0, 1 - distance) ** 2

        # --- SIZE ---
        size = int(ICON_SIZE + (CENTER_SIZE - ICON_SIZE) * t)
        icon = pygame.transform.scale(mask_icons[mask_name], (size, size))

        # --- ROTATION ---
        #rotation = -math.degrees(angle) * 0.8
        #icon = pygame.transform.rotate(icon, rotation)

        # --- OPACITY (FADE OUT) ---
        alpha = int(80 + 175 * t)   # center ≈ 255, sides ≈ 80
        icon.set_alpha(alpha)

        rect = icon.get_rect(center=(x, y))
        screen.blit(icon, rect)





    pygame.display.flip()

# Cleanup
pygame.quit()
sys.exit()