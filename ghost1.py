import pygame
import random
import os
from player import Player
import math

class Ghost:
    def __init__(self, sw, sh):

        self.damage = 10
        self.knockback = 500
        self.hit_cooldown = 700  # ms
        self.alive = True


        # --- knockback velocity (same idea as Player) ---
        self.vx = 0.0
        self.vy = 0.0
        self.knockback_friction = 6.0   # how fast knockback decays



        self.max_health = 40
        self.health = self.max_health   

        self.sw = sw
        self.sh = sh
        
        # Random Spawn at Corners
        corners = [(50, 50), (sw-50, 50), (50, sh-50), (sw-50, sh-50)]
        self.x, self.y = random.choice(corners)
        
        self.speed = 2
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

        # 🔴 Hit flash
        self.last_hit_time = 0
        self.hit_flash_duration = 120  # ms

        # Colors
        self.normal_body_color = self.body_color
        self.hit_body_color = (255, 60, 60)

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
    
    def take_damage(self, dmg):
        now = pygame.time.get_ticks()

        self.health -= dmg
        self.last_hit_time = now   # record hit time

        if self.health <= 0:
            self.alive = False

    def apply_knockback(self, source_x, source_y, force):
        dx = self.x - source_x
        dy = self.y - source_y
        dist = math.hypot(dx, dy) or 1.0
        nx, ny = dx / dist, dy / dist

        # apply impulse (velocity-based)
        self.vx += nx * force
        self.vy += ny * force * 0.9



    def update(self, player: Player):



        px, py = player.rect.center
        dx = px - self.x
        dy = py - self.y


        # Move on ONE axis only (stronger axis)
        if abs(dx) > abs(dy):
            self.x += self.speed if dx > 0 else -self.speed
            self.direction = "RIGHT" if dx > 0 else "LEFT"
        else:
            self.y += self.speed if dy > 0 else -self.speed
            self.direction = "DOWN" if dy > 0 else "UP"
        # --- apply knockback velocity ---
        self.x += self.vx
        self.y += self.vy

        # decay knockback (same idea as Player)
        self.vx *= max(0.0, 1.0 - self.knockback_friction * 0.016)
        self.vy *= max(0.0, 1.0 - self.knockback_friction * 0.016)

        # snap tiny values to zero
        if abs(self.vx) < 0.1:
            self.vx = 0.0
        if abs(self.vy) < 0.1:
            self.vy = 0.0



        # Boundary Check
        margin = 30
        if self.x < margin or self.x > self.sw - margin or self.y < margin or self.y > self.sh - margin:
            self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            self.x = max(margin, min(self.x, self.sw - margin))
            self.y = max(margin, min(self.y, self.sh - margin))

        

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
        ghost_rect = pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )

        player_rect = player.get_rect()
        now = pygame.time.get_ticks()

        self.rect = pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )


        if ghost_rect.colliderect(player_rect):
            if now - self.last_hit_time > self.hit_cooldown:
                if not player.is_invulnerable():
                    self.last_hit_time = now
                    self.hit_player(player)
    

    def draw(self, surface):

        now = pygame.time.get_ticks()

        # 🔴 Flash red if recently hit
        if now - self.last_hit_time < self.hit_flash_duration:
            body_color = self.hit_body_color
        else:
            body_color = self.normal_body_color



        tx, ty = int(self.x - self.size//2), int(self.y - self.size//2)
        s = self.size

        # Pixel Body
        pygame.draw.rect(surface, body_color, (tx, ty + 8, s, s - 16))
        pygame.draw.rect(surface, body_color, (tx + 4, ty + 4, s - 8, 4))
        pygame.draw.rect(surface, body_color, (tx + 8, ty, s - 16, 4))

        # Bottom Curves (Teeth)
        if self.anim_frame == 0:
            pygame.draw.rect(surface, body_color, (tx, ty + s - 8, 8, 8))
            pygame.draw.rect(surface, body_color, (tx + 12, ty + s - 8, 8, 8))
            pygame.draw.rect(surface, body_color, (tx + 24, ty + s - 8, 8, 8))
        else:
            pygame.draw.rect(surface, body_color, (tx + 4, ty + s - 8, 8, 8))
            pygame.draw.rect(surface, body_color, (tx + 20, ty + s - 8, 8, 8))

        # Eyes
        off = {"UP": (0, -3), "DOWN": (0, 3), "LEFT": (-3, 0), "RIGHT": (3, 0)}
        ox, oy = off[self.direction]
        pygame.draw.rect(surface, self.eye_white, (tx + 4, ty + 6, 10, 10))
        pygame.draw.rect(surface, self.eye_white, (tx + 18, ty + 6, 10, 10))
        pygame.draw.rect(surface, self.pupil_red, (tx + 6 + ox, ty + 8 + oy, 5, 5))
        pygame.draw.rect(surface, self.pupil_red, (tx + 20 + ox, ty + 8 + oy, 5, 5))
    def hit_player(self, player):
        # Damage
        player.take_damage(self.damage)

        # Apply realistic, velocity-based knockback (player handles decay & stun)
        player.apply_knockback(self.x, self.y, self.knockback, stun_time=0.18)




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
            g.update(player)
            g.draw(win)
        

        


        

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()