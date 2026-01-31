import pygame
import random
import os

class Ghost:
    def __init__(self, sw, sh):
        self.sw = sw
        self.sh = sh
        
        # Random Spawn at Corners
        corners = [(50, 50), (sw-50, 50), (50, sh-50), (sw-50, sh-50)]
        self.x, self.y = random.choice(corners)
        
        self.speed = random.randint(2, 4)
        self.size = 32
        self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.change_dir_timer = 0
        
        # Animation
        self.anim_frame = 0
        self.anim_timer = 0
        
        # Colors
        g = random.randint(100, 150)
        self.body_color = (g, g, g)
        self.eye_white = (255, 255, 255)
        self.pupil_red = (200, 0, 0)

        # --- Audio Logic ---
        self.sound = None
        try:
            # Loading sound from the sounds folder
            self.sound = pygame.mixer.Sound(os.path.join("sounds", "ghost1so.wav"))
            self.sound_length = int(self.sound.get_length() * 1000) # Length in ms
            self.break_time = 1000 # 1 second break
            # Timer to track when to play next
            self.sound_timer = pygame.time.get_ticks() 
            # Play immediately on spawn
            self.sound.play()
        except:
            self.sound = None

    def update(self):
        # 1. Movement Logic
        if self.direction == "UP": self.y -= self.speed
        elif self.direction == "DOWN": self.y += self.speed
        elif self.direction == "LEFT": self.x -= self.speed
        elif self.direction == "RIGHT": self.x += self.speed

        # Boundary Check
        margin = 30
        if self.x < margin or self.x > self.sw - margin or self.y < margin or self.y > self.sh - margin:
            self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            self.x = max(margin, min(self.x, self.sw - margin))
            self.y = max(margin, min(self.y, self.sh - margin))

        # 2. Random Turn Logic
        self.change_dir_timer += 1
        if self.change_dir_timer > 90:
            self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            self.change_dir_timer = 0

        # 3. Animation Toggle
        self.anim_timer += 1
        if self.anim_timer > 10:
            self.anim_frame = 1 - self.anim_frame
            self.anim_timer = 0

        # 4. Sound Loop with 1s Break
        if self.sound:
            now = pygame.time.get_ticks()
            # If (Sound Length + 1s Break) has passed, play again
            if now - self.sound_timer > (self.sound_length + self.break_time):
                self.sound.play()
                self.sound_timer = now

    def draw(self, surface):
        tx, ty = int(self.x - self.size//2), int(self.y - self.size//2)
        s = self.size

        # Pixel Body
        pygame.draw.rect(surface, self.body_color, (tx, ty + 8, s, s - 16))
        pygame.draw.rect(surface, self.body_color, (tx + 4, ty + 4, s - 8, 4))
        pygame.draw.rect(surface, self.body_color, (tx + 8, ty, s - 16, 4))

        # Bottom Curves (Teeth)
        if self.anim_frame == 0:
            pygame.draw.rect(surface, self.body_color, (tx, ty + s - 8, 8, 8))
            pygame.draw.rect(surface, self.body_color, (tx + 12, ty + s - 8, 8, 8))
            pygame.draw.rect(surface, self.body_color, (tx + 24, ty + s - 8, 8, 8))
        else:
            pygame.draw.rect(surface, self.body_color, (tx + 4, ty + s - 8, 8, 8))
            pygame.draw.rect(surface, self.body_color, (tx + 20, ty + s - 8, 8, 8))

        # Eyes
        off = {"UP": (0, -3), "DOWN": (0, 3), "LEFT": (-3, 0), "RIGHT": (3, 0)}
        ox, oy = off[self.direction]
        pygame.draw.rect(surface, self.eye_white, (tx + 4, ty + 6, 10, 10))
        pygame.draw.rect(surface, self.eye_white, (tx + 18, ty + 6, 10, 10))
        pygame.draw.rect(surface, self.pupil_red, (tx + 6 + ox, ty + 8 + oy, 5, 5))
        pygame.draw.rect(surface, self.pupil_red, (tx + 20 + ox, ty + 8 + oy, 5, 5))

# --- Main Spawner Logic ---
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    
    WIDTH, HEIGHT = 800, 600
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    ghosts = []
    ghosts.append(Ghost(WIDTH, HEIGHT)) # First ghost
    
    spawn_timer = 0
    SPAWN_DELAY = 5000 # 5 seconds
    MAX_GHOSTS = 6

    run = True
    while run:
        win.fill((10, 10, 15))
        dt = clock.get_time()
        spawn_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False

        # Spawn logic
        if len(ghosts) < MAX_GHOSTS and spawn_timer >= SPAWN_DELAY:
            ghosts.append(Ghost(WIDTH, HEIGHT))
            spawn_timer = 0

        # Update and Draw
        for g in ghosts:
            g.update()
            g.draw(win)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()