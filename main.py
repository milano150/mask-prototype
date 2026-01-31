import pygame
import sys
from player import Player, BAR_WIDTH, BAR_HEIGHT
import math
from ghost1 import Ghost

# Initialize pygame
pygame.init()
pygame.mixer.init()


font = pygame.font.Font("assets/fonts/MinecraftRegular-Bmg3.otf", 25)
death_font = pygame.font.Font("assets/fonts/MinecraftRegular-Bmg3.otf", 80)


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

ghosts = []
fireballs = []
ghosts.append(Ghost(WIDTH, HEIGHT))

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
        ghosts.append(Ghost(WIDTH, HEIGHT))
        spawn_timer = 0


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


    keys = pygame.key.get_pressed()
    player.update(keys, dt)
    # ⚔️ Sword damage + debug during swing
    if player.current_mask == "kali" and player.sword_swinging:
        player.sword_attack(ghosts, debug_surface=screen)


    for g in ghosts:
        g.update(player)
    for i in range(len(ghosts)):
        for j in range(i + 1, len(ghosts)):
            g1 = ghosts[i]
            g2 = ghosts[j]

            r1 = pygame.Rect(
                g1.x - g1.size // 2,
                g1.y - g1.size // 2,
                g1.size,
                g1.size
            )
            r2 = pygame.Rect(
                g2.x - g2.size // 2,
                g2.y - g2.size // 2,
                g2.size,
                g2.size
            )

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

        if fireball.is_dead(WIDTH) or not fireball.alive:
            fireballs.remove(fireball)

    
    ghosts = [g for g in ghosts if g.alive]





    screen.fill((20, 20, 20))
    if player.dead:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        text = death_font.render("YOU DIED", True, (200, 0, 0))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, rect)

        pygame.display.flip()
        continue


    player.draw(screen)
    for fireball in fireballs:
        fireball.draw(screen)


    for g in ghosts:
        g.draw(screen)


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
