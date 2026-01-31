import pygame
import sys
from player import Player, BAR_WIDTH, BAR_HEIGHT
import math
from ghost1 import Ghost
from maps.castle import load_castle, SpriteSheet, TILE_SIZE
import random


# Initialize pygame
pygame.init()
pygame.mixer.init()


font = pygame.font.Font("assets/fonts/MinecraftRegular-Bmg3.otf", 25)
death_font = pygame.font.Font("assets/fonts/MinecraftRegular-Bmg3.otf", 80)


# Create window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mask Game")

# --- LOAD CASTLE MAP ---
game_map, walls, spawn = load_castle()

# --- LOAD MAP TILES ---
castle_sheet = SpriteSheet("maps/castle.png")
cave_sheet = SpriteSheet("maps/cave.png")
wall_tile = castle_sheet.get_sprite(120, 60)
floor_tile = cave_sheet.get_sprite(16, 16)


health_bar_img = pygame.image.load("assets/healthbar.png").convert_alpha()

# --- MASK UI SETUP ---
mask_icons = {
    "theyyam": pygame.image.load("assets/theyyam.png").convert_alpha(),
    "garuda": pygame.image.load("assets/garuda.png").convert_alpha(),
    "kali": pygame.image.load("assets/kali.png").convert_alpha(),
}

wheel_image = pygame.image.load("assets/wheel2.png").convert_alpha()
wheel_image.set_alpha(90)

WHEEL_UI_SIZE = 300
wheel_image = pygame.transform.scale(wheel_image, (WHEEL_UI_SIZE, WHEEL_UI_SIZE))

hotbar_img = pygame.image.load("assets/hotbar.png").convert_alpha()

FRAME_W = 64
FRAME_H = 64

hotbar_normal = hotbar_img.subsurface(pygame.Rect(0, 0, FRAME_W, FRAME_H))
hotbar_gold   = hotbar_img.subsurface(pygame.Rect(0, FRAME_H, FRAME_W, FRAME_H))

HOTBAR_SCALE = 4.5  # tweak size here

hotbar_normal = pygame.transform.scale(
    hotbar_normal, (FRAME_W * HOTBAR_SCALE, FRAME_H * HOTBAR_SCALE)
)
hotbar_gold = pygame.transform.scale(
    hotbar_gold, (FRAME_W * HOTBAR_SCALE, FRAME_H * HOTBAR_SCALE)
)


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

mask_order = ["theyyam", "garuda", "kali"]

clock = pygame.time.Clock()
FPS = 60

player = Player(*spawn)


ghosts = []
fireballs = []
ghosts.append(Ghost(
    spawn[0] + random.randint(-200, 200),
    spawn[1] + random.randint(-200, 200)
))


MAX_GHOSTS = 6
SPAWN_DELAY = 5000
spawn_timer = 0



# Main loop
running = True
while running:
    dt = clock.tick(FPS) / 1000
    wheel_offset += (wheel_target - wheel_offset) * 8 * dt

    if mask_name_timer > 0:
        mask_name_timer -= dt

    spawn_timer += dt * 1000  # convert to ms

    if len(ghosts) < MAX_GHOSTS and spawn_timer >= SPAWN_DELAY:
        ghosts.append(Ghost(
            spawn[0] + random.randint(-200, 200),
            spawn[1] + random.randint(-200, 200)
        ))

        spawn_timer = 0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            can_switch = player.mask_switch_cd <= 0  # gold hotbar
            if event.key == pygame.K_1 and can_switch:
                player.change_mask("theyyam")
                player.mask_switch_cd = player.mask_switch_delay
                mask_name_timer = MASK_NAME_DURATION + MASK_NAME_FADE
                wheel_target = mask_order.index("theyyam") 

            if event.key == pygame.K_2 and can_switch:
                player.change_mask("garuda")
                player.mask_switch_cd = player.mask_switch_delay
                mask_name_timer = MASK_NAME_DURATION + MASK_NAME_FADE
                wheel_target = mask_order.index("garuda") 

            if event.key == pygame.K_3 and can_switch:
                player.change_mask("kali")
                player.mask_switch_cd = player.mask_switch_delay
                mask_name_timer = MASK_NAME_DURATION + MASK_NAME_FADE
                wheel_target = mask_order.index("kali") 


            if event.key == pygame.K_h:
                player.take_damage(10)

            if event.key == pygame.K_SPACE:
                # 🔥 Fireball (Theyyam)
                if player.current_mask == "theyyam":
                    fireball = player.shoot_fireball()
                    if fireball:
                        fireballs.append(fireball)

                # ⚔️ Sword (Kali)
                elif player.current_mask == "kali":
                    if not player.sword_swinging:
                        player.sword_swinging = True
                        player.sword_timer = player.sword_duration
                        player.sword_angle = 90 if player.facing == 1 else -105
            if player.dead and event.key == pygame.K_r:
                # Reset player
                player.respawn(*spawn)

                # Reset enemies & projectiles
                ghosts.clear()
                fireballs.clear()

                ghosts.append(Ghost(
                    spawn[0] + random.randint(-150, 150),
                    spawn[1] + random.randint(-150, 150)
                ))

                

                spawn_timer = 0


    keys = pygame.key.get_pressed()
    old_rect = player.rect.copy()
    player.update(keys, dt)
    for wall in walls:
        if player.rect.colliderect(wall):
            player.rect = old_rect
            break

    # ⚔️ Sword damage + debug during swing
    if player.current_mask == "kali" and player.sword_swinging:
        player.sword_attack(ghosts, debug_surface=screen)


    for g in ghosts:
        g.update(player, dt)
    for i in range(len(ghosts)):
        for j in range(i + 1, len(ghosts)):
            g1 = ghosts[i]
            g2 = ghosts[j]

            r1 = g1.rect
            r2 = g2.rect

            if r1.colliderect(r2):
                push = 6
                g1.apply_knockback(g2.x, g2.y, push)
                g2.apply_knockback(g1.x, g1.y, push)


    for fireball in fireballs[:]:
        fireball.update(dt)

        for ghost in ghosts:
            if ghost.alive and fireball.hitbox.colliderect(ghost.rect):
                ghost.take_damage(fireball.damage)

                # 🔥 FIREBALL KNOCKBACK
                ghost.apply_knockback(
                    fireball.hitbox.centerx,
                    fireball.hitbox.centery,
                    14  # fireball knockback force
                )

                fireball.alive = False
                break

        if fireball.is_dead():
            fireballs.remove(fireball)


    
    ghosts = [g for g in ghosts if g.alive]


    camera_x = player.rect.centerx - WIDTH // 2
    camera_y = player.rect.centery - HEIGHT // 2


    # --- DRAW MAP ---
    screen.fill((20, 20, 20))
    for r, row in enumerate(game_map):
        for c, char in enumerate(row):
            x = c * TILE_SIZE - camera_x
            y = r * TILE_SIZE - camera_y
            screen.blit(floor_tile, (x, y))
            if char == "W":
                screen.blit(wall_tile, (x, y))

    if player.dead:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0, 160))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        text = death_font.render("YOU DIED", True, (200, 0, 0))
        subtext = font.render("     press R to respawn", True, (200, 200, 200))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        rect2 = text.get_rect(center=(WIDTH // 2, (HEIGHT // 2)+90))
        screen.blit(text, rect)
        screen.blit(subtext, rect2)

        pygame.display.flip()
        continue


    player.draw(screen, (camera_x, camera_y))

    for fireball in fireballs:
        fireball.draw(screen, (camera_x, camera_y))


    for g in ghosts:
        g.draw(screen, (camera_x, camera_y))


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
    #screen.blit(wheel_image, wheel_rect)
    is_ready = player.mask_switch_cd <= 0

    # Base hotbar
    hotbar_base = hotbar_gold if is_ready else hotbar_normal
    hotbar = hotbar_base.copy()

    # Base opacity
    hotbar.set_alpha(140 if not is_ready else 210)

    hb_rect = hotbar.get_rect(
        midbottom=wheel_rect.midbottom
    )
    screen.blit(hotbar, hb_rect)



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

        # 🎠 CAROUSEL ROTATION (exact behavior)
        rotation = 0  
        icon = pygame.transform.rotate(icon, rotation)

        alpha = int(80 + 175 * t)
        icon.set_alpha(alpha)

        rect = icon.get_rect(center=(x, y))
        screen.blit(icon, rect)


    pygame.display.flip()

pygame.quit()
sys.exit()
