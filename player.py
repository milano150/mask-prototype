import pygame
import math
import random
from fireball import Fireball

# =====================
# HEALTH BAR CONSTANTS
# =====================
BAR_WIDTH = 64
BAR_HEIGHT = 64
TOTAL_FRAMES = 13
COLUMNS = 3


class HealthBar:
    def __init__(self, max_health):
        self.max_health = max_health
        self.step = max_health / TOTAL_FRAMES
        self.current_step = 0

    def take_damage(self, amount):
        steps_lost = round(amount / self.step)
        self.current_step = min(
            TOTAL_FRAMES - 1,
            self.current_step + max(1, steps_lost)
        )

    def heal(self, amount):
        steps_gained = round(amount / self.step)
        self.current_step = max(
            0,
            self.current_step - max(1, steps_gained)
        )

    def get_frame_rect(self):
        frame_index = self.current_step
        col = frame_index % COLUMNS
        row = frame_index // COLUMNS
        return pygame.Rect(
            col * BAR_WIDTH,
            row * BAR_HEIGHT,
            BAR_WIDTH,
            BAR_HEIGHT
        )


# =====================
# COLORS
# =====================
SKIN = (255, 180, 130)
BEARD_BROWN = (60, 30, 10)
SHIRT_DARK = (40, 40, 40)
PANTS_BROWN = (100, 50, 20)
EYE_BLUE = (10, 10, 10)
BOOT_COLOR = (45, 30, 20)
DUST_COLOR = (200, 200, 200)
GOLD, RED, BLUE, YELLOW = (218, 165, 32), (200, 0, 0), (30, 60, 180), (255, 215, 0)


# =====================
# DUST PARTICLE
# =====================
class Dust:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.size = random.randint(2, 4)
        self.life = 25
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-0.5, -1)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(
                surface, DUST_COLOR,
                (int(self.x), int(self.y)), self.size
            )


# =====================
# PLAYER
# =====================
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 20, y - 50, 40, 105)

        self.masks = {
            "theyyam": {"speed": 200},
            "bhairava": {"speed": 200},
            "kali": {"speed": 200},
        }

        self.current_mask = "theyyam"
        self.speed = self.masks[self.current_mask]["speed"]

        self.health_bar = HealthBar(100)

        # Movement / view
        self.facing = 1          # 1 = right, -1 = left
        self.view = "FRONT"
        self.walk_count = 0
        self.dust_particles = []

        # Fireballs (Theyyam)
        self.fireballs = []
        self.fireball_cooldown = 0.8
        self.fireball_timer = 0.0

        # Sword (Kali)
        self.sword_img = pygame.image.load("assets/sword.png").convert_alpha()
        self.sword_img = pygame.transform.scale(
            self.sword_img,
            (self.sword_img.get_width() * 3,
             self.sword_img.get_height() * 3)
        )
        self.sword_img = pygame.transform.rotate(self.sword_img, -90)
        self.sword_angle = 0
        self.sword_swinging = False
        self.sword_timer = 0
        self.sword_duration = 12

    # -----------------
    # MASK
    # -----------------
    def change_mask(self, mask_name):
        if mask_name in self.masks:
            self.current_mask = mask_name
            self.speed = self.masks[mask_name]["speed"]

    # -----------------
    # COMBAT
    # -----------------
    def shoot_fireball(self):
        if self.current_mask != "theyyam":
            return
        if self.fireball_timer > 0:
            return

        self.fireballs.append(
            Fireball(self.rect.centerx, self.rect.centery, self.facing)
        )
        self.fireball_timer = self.fireball_cooldown

    def take_damage(self, amount):
        self.health_bar.take_damage(amount)

    # -----------------
    # UPDATE
    # -----------------
    def update(self, keys, dt):
        dx = dy = 0
        moving = False

        if keys[pygame.K_a]:
            dx -= 1
            self.facing = -1
            self.view = "LEFT"
            moving = True
        if keys[pygame.K_d]:
            dx += 1
            self.facing = 1
            self.view = "RIGHT"
            moving = True
        if keys[pygame.K_w]:
            dy -= 1
            self.view = "BACK"
            moving = True
        if keys[pygame.K_s]:
            dy += 1
            self.view = "FRONT"
            moving = True

        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length

        # -------- MOVE X --------
        self.rect.x += dx * self.speed * dt

        # -------- MOVE Y --------
        self.rect.y += dy * self.speed * dt
  


        if moving:
            self.walk_count += 0.2
            if random.random() > 0.6:
                self.dust_particles.append(
                    Dust(self.rect.centerx, self.rect.bottom - 5)
                )
        else:
            self.walk_count = 0

        for d in self.dust_particles[:]:
            d.update()
            if d.life <= 0:
                self.dust_particles.remove(d)

        # Fireballs
        if self.fireball_timer > 0:
            self.fireball_timer -= dt

        for f in self.fireballs:
            f.update(dt)

        self.fireballs = [f for f in self.fireballs if not f.is_dead(800)]

        # Sword animation
        if self.sword_swinging:
            self.sword_timer -= 1
            if self.facing == 1:
                self.sword_angle -= 6
            else:
                self.sword_angle += 6

            if self.sword_timer <= 0:
                self.sword_swinging = False
                self.sword_angle = 0

    # -----------------
    # MASK HEAD
    # -----------------
    def draw_mask_head(self, surface, x, y, view):
        mx, my = x, y + 5

        if self.current_mask == "theyyam":
            base_c, face_c = GOLD, RED
        elif self.current_mask == "bhairava":
            base_c, face_c = RED, YELLOW
        else:  # kali
            base_c, face_c = (192, 192, 192), BLUE

        if view == "FRONT":
            pygame.draw.circle(surface, base_c, (mx, my), 28)
            pygame.draw.rect(surface, face_c, (mx - 15, my - 12, 30, 35), border_radius=2)
            pygame.draw.circle(surface, (10, 10, 10), (mx - 7, my + 2), 4)
            pygame.draw.circle(surface, (10, 10, 10), (mx + 7, my + 2), 4)

        elif view == "BACK":
            pygame.draw.circle(surface, base_c, (mx, my), 24)
            pygame.draw.rect(surface, face_c, (mx - 12, my - 5, 24, 28), border_radius=2)

        else:  # SIDE
            is_right = (view == "RIGHT")
            side_x = mx + 2 if is_right else mx - 12
            pygame.draw.rect(
                surface,
                base_c,
                (mx + (10 if is_right else -14), my - 20, 4, 15),
                border_radius=1
            )
            pygame.draw.rect(surface, face_c, (side_x, my - 12, 10, 32), border_radius=2)
            eye_x = mx + 6 if is_right else mx - 8
            pygame.draw.circle(surface, (10, 10, 10), (eye_x, my + 2), 3)

    # -----------------
    # DRAW
    # -----------------
    def draw(self, screen, camera_offset=(0, 0)):
        x, y = self.rect.x, self.rect.y
        bob = math.sin(self.walk_count) * 3
        leg_step = math.sin(self.walk_count) * 6

        cx, cy = camera_offset
        x = self.rect.x - cx
        y = self.rect.y - cy

        for d in self.dust_particles:
            d.draw(screen)

        # --- BODY ---
        if self.view == "FRONT":
            pygame.draw.rect(screen, BEARD_BROWN, (x + 8, y + bob, 24, 25), border_radius=5)
            pygame.draw.rect(screen, SHIRT_DARK, (x + 6, y + 35 + bob, 28, 30))

            pygame.draw.rect(screen, SKIN, (x + 2, y + 35 + bob, 4, 18))
            pygame.draw.rect(screen, SKIN, (x + 34, y + 35 + bob, 4, 18))
            pygame.draw.rect(screen, SKIN, (x + 1, y + 53 + bob, 6, 6))
            pygame.draw.rect(screen, SKIN, (x + 33, y + 53 + bob, 6, 6))

            pygame.draw.rect(screen, PANTS_BROWN, (x + 8, y + 65, 10, 20 + leg_step))
            pygame.draw.rect(screen, PANTS_BROWN, (x + 22, y + 65, 10, 20 - leg_step))
            pygame.draw.rect(screen, BOOT_COLOR, (x + 7, y + 85 + leg_step, 12, 8), border_radius=2)
            pygame.draw.rect(screen, BOOT_COLOR, (x + 21, y + 85 - leg_step, 12, 8), border_radius=2)

        elif self.view == "BACK":
            pygame.draw.rect(screen, BEARD_BROWN, (x + 8, y + bob, 24, 30))
            pygame.draw.rect(screen, SHIRT_DARK, (x + 6, y + 35 + bob, 28, 30))

            pygame.draw.rect(screen, SKIN, (x + 3, y + 35 + bob, 4, 18))
            pygame.draw.rect(screen, SKIN, (x + 33, y + 35 + bob, 4, 18))
            pygame.draw.rect(screen, SKIN, (x + 2, y + 53 + bob, 6, 6))
            pygame.draw.rect(screen, SKIN, (x + 32, y + 53 + bob, 6, 6))

            pygame.draw.rect(screen, PANTS_BROWN, (x + 8, y + 65, 10, 20 + leg_step))
            pygame.draw.rect(screen, PANTS_BROWN, (x + 22, y + 65, 10, 20 - leg_step))
            pygame.draw.rect(screen, BOOT_COLOR, (x + 7, y + 85 + leg_step, 12, 8), border_radius=2)
            pygame.draw.rect(screen, BOOT_COLOR, (x + 21, y + 85 - leg_step, 12, 8), border_radius=2)

        else:  # LEFT / RIGHT
            is_right = self.view == "RIGHT"
            pygame.draw.rect(screen, BEARD_BROWN, (x + 12, y + bob, 16, 30))
            pygame.draw.rect(screen, SHIRT_DARK, (x + 14, y + 35 + bob, 12, 30))

            arm_x = x + 24 if is_right else x + 10
            pygame.draw.rect(screen, SKIN, (arm_x, y + 38 + bob, 5, 15))
            pygame.draw.rect(screen, SKIN, (arm_x - 1, y + 53 + bob, 7, 6))

            pygame.draw.rect(screen, PANTS_BROWN, (x + 14, y + 65, 6, 20 + leg_step))
            pygame.draw.rect(screen, PANTS_BROWN, (x + 20, y + 65, 6, 20 - leg_step))
            pygame.draw.rect(screen, BOOT_COLOR, (x + 14, y + 85 + leg_step, 12, 8))

        # --- MASK ---
        self.draw_mask_head(screen, x + 20, y + bob + 5, self.view)

        # --- FIREBALLS ---
        for f in self.fireballs:
            f.draw(screen)

        # --- SWORD ---
        if self.current_mask == "kali" and self.sword_swinging:
            sword_img = self.sword_img
            if self.facing == -1:
                sword_img = pygame.transform.flip(sword_img, True, False)

            rotated = pygame.transform.rotate(sword_img, self.sword_angle)
            offset_x = 22 if self.facing == 1 else -22
            rect = rotated.get_rect(
                center=(self.rect.centerx + offset_x, self.rect.centery)
            )
            screen.blit(rotated, rect)
