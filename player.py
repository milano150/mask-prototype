import pygame
import math
from fireball import Fireball

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
