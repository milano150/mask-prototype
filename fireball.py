import pygame

import pygame

class Fireball:
    def __init__(self, x, y, direction):
        self.image = pygame.image.load("assets/fireball2.png").convert_alpha()

        self.direction = direction  # -1 = left, 1 = right
        self.speed = 600
        self.lifetime = 1.5

        # Flip image if going left
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt):
        self.rect.x += self.direction * self.speed * dt
        self.lifetime -= dt

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_dead(self, width):
        return self.lifetime <= 0 or self.rect.right < 0 or self.rect.left > width

