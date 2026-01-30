import pygame
import math

class Player:
    def __init__(self, x, y):
        self.size = 40
        self.rect = pygame.Rect(x, y, self.size, self.size)

        # --- MASK SYSTEM (speed = pixels per second) ---
        self.masks = {
            "theyyam": {"speed": 300, "color": (50, 200, 255)},
            "bhairava": {"speed": 450, "color": (50, 255, 100)},
            "kali": {"speed": 180, "color": (200, 50, 50)}
        }

        self.current_mask = "theyyam"
        self.speed = self.masks[self.current_mask]["speed"]
        self.color = self.masks[self.current_mask]["color"]

    def change_mask(self, mask_name):
        if mask_name in self.masks:
            self.current_mask = mask_name
            self.speed = self.masks[mask_name]["speed"]
            self.color = self.masks[mask_name]["color"]
            print(f"Mask changed to: {mask_name}")

    def update(self, keys, dt):
        dx = 0
        dy = 0

        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1

        # Normalize diagonal movement
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length

        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
