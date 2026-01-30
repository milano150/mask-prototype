import pygame

def draw(surface, x, y, target_size=(48, 60)):
    w, h = target_size
    sx = w / 120
    sy = h / 150

    BLUE = (30, 60, 180)
    SILVER = (200, 200, 210)
    BLACK = (10, 10, 20)
    WHITE = (255, 255, 255)
    RED = (210, 0, 0)

    def S(px, py):
        return int(x + px * sx), int(y + py * sy)

    # Crown
    pygame.draw.circle(surface, SILVER, S(0, 10), int(63 * sx), draw_top_left=True, draw_top_right=True)
    pygame.draw.circle(surface, BLUE, S(0, 10), int(60 * sx), draw_top_left=True, draw_top_right=True)

    # Face
    face = [
        S(-30, -20), S(30, -20),
        S(38, 10), S(22, 45),
        S(0, 60),
        S(-22, 45), S(-38, 10)
    ]
    pygame.draw.polygon(surface, BLUE, face)
    pygame.draw.polygon(surface, BLACK, face, 2)

    # Eyes
    for ex in (-14, 14):
        pygame.draw.circle(surface, BLACK, S(ex, 10), int(10 * sx))
        pygame.draw.circle(surface, WHITE, S(ex, 10), int(3 * sx))

    # Third eye
    pygame.draw.ellipse(surface, WHITE, (*S(-4, -12), int(8*sx), int(14*sy)))
    pygame.draw.circle(surface, RED, S(0, -5), int(3 * sx))

    # Tongue
    pygame.draw.rect(surface, RED, (*S(-6, 40), int(12*sx), int(24*sy)), border_radius=6)
