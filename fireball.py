import pygame

class Fireball:
    def __init__(self, x, y, direction):
        # 🔥 VISUAL SPRITE (big)
        self.image = pygame.image.load("assets/fireball2.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (128, 128))

        self.direction = direction  # -1 = left, 1 = right
        self.speed = 600            # pixels per second
        self.lifetime = 1.5         # seconds
        self.damage = 20
        self.alive = True

        # Flip image if going left
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        # 🎯 COLLISION HITBOX (small & fair)
        self.hitbox = pygame.Rect(0, 0, 28, 28)
        self.hitbox.center = (x, y)

        # VISUAL rect (only for drawing)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt):
        dx = self.direction * self.speed * dt

        # Move both visual sprite and hitbox
        self.rect.x += dx
        self.hitbox.x += dx

        self.lifetime -= dt

    def draw(self, screen):
        screen.blit(self.image, self.rect)

        # 🔍 DEBUG HITBOX (uncomment if needed)
        pygame.draw.rect(screen, (0, 255, 0), self.hitbox, 1)

    def is_dead(self, screen_width):
        return (
            self.lifetime <= 0
            or self.hitbox.right < 0
            or self.hitbox.left > screen_width
        )
