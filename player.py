import pygame
import math
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

        # Each frame = one health step
        self.step = max_health / TOTAL_FRAMES

        # Start full
        self.current_step = 0  # 0 = full, last = empty

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
# PLAYER
# =====================
class Player:
    def __init__(self, x, y):
        self.size = 40
        self.rect = pygame.Rect(x, y, self.size, self.size)

        self.masks = {
            "theyyam": {"speed": 300, "color": (50, 200, 255)},
            "bhairava": {"speed": 450, "color": (50, 255, 100)},
            "kali": {"speed": 180, "color": (200, 50, 50)},
        }

        self.current_mask = "theyyam"
        self.speed = self.masks[self.current_mask]["speed"]
        self.color = self.masks[self.current_mask]["color"]

        # Health bar (segmented, frame-based)
        self.health_bar = HealthBar(100)

        # Fireballs
        self.fireballs = []
        self.fireball_cooldown = 0.8
        self.fireball_timer = 0.0

        self.facing = 1  # 1 = right, -1 = left

    # -----------------
    # MASK
    # -----------------
    def change_mask(self, mask_name):
        if mask_name not in self.masks:
            return

        self.current_mask = mask_name
        self.speed = self.masks[mask_name]["speed"]
        self.color = self.masks[mask_name]["color"]

    # -----------------
    # COMBAT
    # -----------------
    def shoot_fireball(self):
        if self.current_mask != "theyyam":
            return
        if self.fireball_timer > 0:
            return

        fx = self.rect.centerx
        fy = self.rect.centery
        self.fireballs.append(Fireball(fx, fy, self.facing))
        self.fireball_timer = self.fireball_cooldown

    def take_damage(self, amount):
        self.health_bar.take_damage(amount)

    # -----------------
    # UPDATE
    # -----------------
    def update(self, keys, dt):
        dx = dy = 0

        if keys[pygame.K_a]:
            dx -= 1
            self.facing = -1
        if keys[pygame.K_d]:
            dx += 1
            self.facing = 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1

        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length

        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt

        # Fireball cooldown
        if self.fireball_timer > 0:
            self.fireball_timer -= dt

        # Update fireballs
        for fireball in self.fireballs:
            fireball.update(dt)

        self.fireballs = [
            f for f in self.fireballs if not f.is_dead(800)
        ]

    # -----------------
    # DRAW
    # -----------------
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

        for fireball in self.fireballs:
            fireball.draw(screen)
