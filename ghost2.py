import pygame
import random
import os
import math

class GhostBride:
    def __init__(self, sw, sh, delay_ms=0):
        self.sw, self.sh = sw, sh
        self.x = random.randint(100, sw - 100)
        self.y = random.randint(100, sh - 100)
        
        self.size = 50
        self.speed = 2
        self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        
        # Timing & Delay logic
        self.spawn_time = pygame.time.get_ticks() + delay_ms
        self.has_spawned = False
        
        # Teleport Logic
        self.teleport_count = 0
        self.max_teleports = 2
        self.teleport_interval = 4000 
        self.last_teleport_time = 0
        
        # Alpha and Fading
        self.current_alpha = 0 
        self.is_fading = False

        # Audio initialization
        pygame.mixer.init()
        try:
            self.snd_spawn = pygame.mixer.Sound(os.path.join("sounds", "bride_spawn.wav"))
            self.snd_warn = pygame.mixer.Sound(os.path.join("sounds", "bride_warn.wav"))
        except:
            self.snd_spawn = self.snd_warn = None

    def update(self):
        now = pygame.time.get_ticks()

        # 1. Handle Staggered Spawn
        if not self.has_spawned:
            if now >= self.spawn_time:
                self.has_spawned = True
                self.last_teleport_time = now
                self.current_alpha = 255
                if self.snd_spawn: self.snd_spawn.play()
            return

        # 2. Teleport & Fade Logic
        if self.teleport_count < self.max_teleports:
            time_since = now - self.last_teleport_time
            
            # Fade and warn 1 second before teleporting
            if 3000 < time_since < 4000:
                if not self.is_fading:
                    if self.snd_warn: self.snd_warn.play()
                    self.is_fading = True
                # Fade out with a slight "horror flicker"
                base_fade = 255 - int((time_since - 3000) * 0.25)
                flicker = int(math.sin(now * 0.1) * 30)
                self.current_alpha = max(0, min(255, base_fade + flicker))
            
            if time_since >= self.teleport_interval:
                self.x = random.randint(50, self.sw - 50)
                self.y = random.randint(50, self.sh - 50)
                self.teleport_count += 1
                self.last_teleport_time = now
                self.current_alpha = 255
                self.is_fading = False

        # 3. Movement
        if self.direction == "UP": self.y -= self.speed
        elif self.direction == "DOWN": self.y += self.speed
        elif self.direction == "LEFT": self.x -= self.speed
        elif self.direction == "RIGHT": self.x += self.speed

        if self.x < 20 or self.x > self.sw - 20 or self.y < 20 or self.y > self.sh - 20:
            self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])

    def draw(self, surface):
        if not self.has_spawned: return

        s = self.size
        temp_surf = pygame.Surface((s, s + 20), pygame.SRCALPHA)
        
        # Colors
        frock_white = (230, 230, 235)
        blood_red = (130, 0, 0)
        hair_black = (5, 5, 8)
        skin_pale = (210, 200, 200)
        eye_black = (0, 0, 0)

        # 1. DRAW TAPERED FROCK
        pygame.draw.rect(temp_surf, frock_white, (s//4 + 5, 15, s//2 - 10, 12)) # Bodice
        pygame.draw.polygon(temp_surf, frock_white, [
            (s//4 + 2, 27), (s - s//4 - 2, 27), (s, s + 10), (0, s + 10)
        ]) # Skirt

        # 2. BLOOD SPLATTER
        random.seed(42) # Keeps blood in same spot
        for _ in range(15):
            bx, by = random.randint(s//4, s - s//4), random.randint(27, s + 5)
            pygame.draw.rect(temp_surf, blood_red, (bx, by, 3, 5))
        random.seed()

        # 3. HAIR (Now with 3 sections for more detail)
        pygame.draw.rect(temp_surf, hair_black, (s//4 - 4, 5, 8, s)) # Left
        pygame.draw.rect(temp_surf, hair_black, (s - s//4 - 4, 5, 8, s)) # Right
        pygame.draw.rect(temp_surf, hair_black, (s//4, 0, s//2, 10)) # Top

        # 4. SCARY FACE
        pygame.draw.rect(temp_surf, skin_pale, (s//4 + 4, 8, s//2 - 8, 14))
        # FIXED: Hollow eyes with correct arguments
        pygame.draw.rect(temp_surf, eye_black, (s//4 + 7, 12, 5, 8)) # Left Eye
        pygame.draw.rect(temp_surf, eye_black, (s - s//4 - 12, 12, 5, 8)) # Right Eye (Corrected!)

        temp_surf.set_alpha(self.current_alpha)
        surface.blit(temp_surf, (int(self.x - s//2), int(self.y - s//2)))

# --- Run Test Loop ---
if __name__ == "__main__":
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # 2 Brides, one spawning 4 seconds after the first
    brides = [GhostBride(WIDTH, HEIGHT, 0), GhostBride(WIDTH, HEIGHT, 4000)]

    run = True
    while run:
        win.fill((10, 10, 15))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False

        for b in brides:
            b.update()
            b.draw(win)

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()