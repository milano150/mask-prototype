import pygame
import math

class Fireball:
    def __init__(self, x, y, dir_x, dir_y):

        self.image = pygame.image.load("assets/fireball2.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))

        self.speed = 600
        self.lifetime = 1.5
        self.damage = 20
        self.alive = True

        # Normalize direction (safety)
        length = math.hypot(dir_x, dir_y)
        if length == 0:
            dir_x, dir_y = 1, 0
        else:
            dir_x /= length
            dir_y /= length

        self.vx = dir_x * self.speed
        self.vy = dir_y * self.speed

        # --- ROTATION BASED ON FIRE DIRECTION (4-way only) ---
        if dir_x == 1 and dir_y == 0:        # RIGHT
            angle = 0
        elif dir_x == -1 and dir_y == 0:     # LEFT
            angle = 180
        elif dir_x == 0 and dir_y == -1:     # UP
            angle = 90
        else:                               # DOWN
            angle = -90

        self.image = pygame.transform.rotate(self.image, angle)


        # Hitbox (small & fair)
        self.hitbox = pygame.Rect(0, 0, 16, 16)
        self.hitbox.center = (x, y)

        # Visual rect
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt, walls):
        dx = self.vx * dt
        dy = self.vy * dt

        self.rect.x += dx
        self.rect.y += dy
        self.hitbox.x += dx
        self.hitbox.y += dy

        self.lifetime -= dt

        # 🧱 WALL COLLISION
        for wall in walls:
            if self.hitbox.colliderect(wall):
                self.alive = False
                return

    def draw(self, screen, camera_offset):
        cx, cy = camera_offset
        screen.blit(self.image, self.rect.move(-cx, -cy))

        # Debug hitbox
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            self.hitbox.move(-cx, -cy),
            1
        )

    def is_dead(self):
        return self.lifetime <= 0 or not self.alive
