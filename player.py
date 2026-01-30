import pygame
import math
from fireball import Fireball

BAR_WIDTH = 128     # width of ONE bar frame
BAR_HEIGHT = 16     # height of ONE bar frame
TOTAL_FRAMES = 10   # number of bar states in image

health_bar_img = pygame.image.load("assets/healthbar.png").convert_alpha()

class HealthBar:
    def __init__(self, max_health):
        self.max_health = max_health
        self.current_health = max_health

    def take_damage(self, amount):
        self.current_health = max(0, self.current_health - amount)

    def heal(self, amount):
        self.current_health = min(self.max_health, self.current_health + amount)

    def get_frame_rect(self):
        health_ratio = self.current_health / self.max_health
        frame_index = int((1 - health_ratio) * (TOTAL_FRAMES - 1))
        frame_index = max(0, min(TOTAL_FRAMES - 1, frame_index))

        return pygame.Rect(
            frame_index * BAR_WIDTH,
            0,
            BAR_WIDTH,
            BAR_HEIGHT
        )

class Player:
    def __init__(self, x, y):
        self.size = 40
        self.rect = pygame.Rect(x, y, self.size, self.size)

        self.masks = {
            "theyyam": {"speed": 300, "color": (50, 200, 255)},
            "bhairava": {"speed": 450, "color": (50, 255, 100)},
            "kali": {"speed": 180, "color": (200, 50, 50)}
        }

        self.current_mask = "theyyam"
        self.speed = self.masks[self.current_mask]["speed"]
        self.color = self.masks[self.current_mask]["color"]
        

        self.fireballs = []
        self.fireball_cooldown = 0.8
        self.fireball_timer = 0

        self.facing = 1  # right

    def change_mask(self, mask_name):
        self.current_mask = mask_name
        self.speed = self.masks[mask_name]["speed"]
        self.color = self.masks[mask_name]["color"]

    def shoot_fireball(self):
        if self.current_mask != "theyyam":
            return
        if self.fireball_timer > 0:
            return

        fx = self.rect.centerx
        fy = self.rect.centery
        self.fireballs.append(Fireball(fx, fy, self.facing))
        self.fireball_timer = self.fireball_cooldown

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
        if length:
            dx /= length
            dy /= length

        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt

        if self.fireball_timer > 0:
            self.fireball_timer -= dt

        for fireball in self.fireballs:
            fireball.update(dt)

        self.fireballs = [f for f in self.fireballs if not f.is_dead(800)]

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        for fireball in self.fireballs:
            fireball.draw(screen)
