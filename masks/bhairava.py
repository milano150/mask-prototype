import pygame

def draw(surface, x, y, target_size=(48, 60)):
    w, h = target_size
    sx = w / 120
    sy = h / 150

    YELLOW = (255, 215, 0)
    RED = (200, 0, 0)
    BLACK = (10, 10, 10)
    WHITE = (255, 255, 255)

    def S(px, py):
        return int(x + px * sx), int(y + py * sy)

    # Crown
    pygame.draw.circle(surface, RED, S(0, 10), int(63 * sx), draw_top_left=True, draw_top_right=True)
    pygame.draw.circle(surface, YELLOW, S(0, 10), int(60 * sx), draw_top_left=True, draw_top_right=True)

    # Face
    face = [
        S(-30, -20), S(30, -20),
        S(35, 10), S(20, 45),
        S(0, 60),
        S(-20, 45), S(-35, 10)
    ]
    pygame.draw.polygon(surface, YELLOW, face)
    pygame.draw.polygon(surface, BLACK, face, 2)

    # Eyes
    for ex in (-12, 12):
        pygame.draw.circle(surface, BLACK, S(ex, 10), int(9 * sx))
        pygame.draw.circle(surface, WHITE, S(ex, 10), int(3 * sx))

    # Third eye
    pygame.draw.ellipse(surface, WHITE, (*S(-4, -12), int(8*sx), int(14*sy)))

    # Mustache
    pygame.draw.arc(surface, BLACK, (*S(-28, 30), int(28*sx), int(18*sy)), 3.14, 0, 4)
    pygame.draw.arc(surface, BLACK, (*S(0, 30), int(28*sx), int(18*sy)), 3.14, 0, 4)
