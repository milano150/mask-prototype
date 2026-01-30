import pygame

class Player:
    def __init__(self, x, y):
        self.size = 40
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.speed = 5
        self.color = (50, 200, 255)

    def update(self, keys):
        dx = 0
        dy = 0

        if keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_s]:
            dy += self.speed
        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed

        self.rect.x += dx
        self.rect.y += dy

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)