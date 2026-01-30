import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Theyyam Hackathon - Complete 360 View")
clock = pygame.time.Clock()

# --- COLORS ---
SKIN = (255, 180, 130)
BEARD_BROWN = (60, 30, 10)
SHIRT_DARK = (40, 40, 40)
PANTS_BROWN = (100, 50, 20)
EYE_BLUE = (10, 10, 10)
BOOT_COLOR = (45, 30, 20)
DUST_COLOR = (200, 200, 200)
GOLD, RED, BLUE, YELLOW = (218, 165, 32), (200, 0, 0), (30, 60, 180), (255, 215, 0)

MASKS = ["None", "Guardian", "Bhairava", "Kaali"]

class Dust:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.size = random.randint(2, 5)
        self.life = 25
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-0.5, -1)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, DUST_COLOR, (int(self.x), int(self.y)), int(self.size))

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 20, y - 50, 40, 105)
        self.speed = 4
        self.view = "FRONT" 
        self.mask_index = 0
        self.walk_count = 0
        self.dust_particles = []

    def move(self):
        keys = pygame.key.get_pressed()
        moving = False
        if keys[pygame.K_a]: self.rect.x -= self.speed; self.view = "LEFT"; moving = True
        elif keys[pygame.K_d]: self.rect.x += self.speed; self.view = "RIGHT"; moving = True
        elif keys[pygame.K_w]: self.rect.y -= self.speed; self.view = "BACK"; moving = True
        elif keys[pygame.K_s]: self.rect.y += self.speed; self.view = "FRONT"; moving = True
        
        if moving:
            self.walk_count += 0.2
            if random.random() > 0.6:
                self.dust_particles.append(Dust(self.rect.centerx, self.rect.bottom - 5))
        else:
            self.walk_count = 0
        
        for d in self.dust_particles[:]:
            d.update()
            if d.life <= 0: self.dust_particles.remove(d)
        self.rect.clamp_ip(screen.get_rect())

    def draw_mask_head(self, surface, x, y, mask_type, view):
        mx, my = x, y + 5
        base_c = GOLD if mask_type == "Guardian" else RED if mask_type == "Bhairava" else (192, 192, 192)
        face_c = RED if mask_type == "Guardian" else YELLOW if mask_type == "Bhairava" else BLUE
        
        if view == "FRONT":
            pygame.draw.circle(surface, base_c, (mx, my), 28, draw_top_left=True, draw_top_right=True)
            pygame.draw.rect(surface, face_c, (mx - 15, my - 12, 30, 35), border_radius=2)
            pygame.draw.circle(surface, (10, 10, 10), (mx - 7, my + 2), 4)
            pygame.draw.circle(surface, (10, 10, 10), (mx + 7, my + 2), 4)
        elif view == "BACK":
            # Crown visible from back
            pygame.draw.circle(surface, base_c, (mx, my), 24, draw_top_left=True, draw_top_right=True)
            pygame.draw.rect(surface, face_c, (mx - 12, my - 5, 24, 28), border_radius=2)
        else: # SIDE
            is_right = (view == "RIGHT")
            side_x = mx + 2 if is_right else mx - 12
            pygame.draw.rect(surface, base_c, (mx + (10 if is_right else -14), my - 20, 4, 15), border_radius=1)
            pygame.draw.rect(surface, face_c, (side_x, my - 12, 10, 32), border_radius=2)
            eye_x = mx + 6 if is_right else mx - 8
            pygame.draw.circle(surface, (10,10,10), (eye_x, my + 2), 3)

    def draw(self, surface):
        x, y = self.rect.x, self.rect.y
        bob = math.sin(self.walk_count) * 3
        leg_step = math.sin(self.walk_count) * 6
        
        for d in self.dust_particles: d.draw(surface)

        current_mask = MASKS[self.mask_index]
        mask_face_color = RED if current_mask == "Guardian" else YELLOW if current_mask == "Bhairava" else BLUE
        active_hair_color = mask_face_color if current_mask != "None" else BEARD_BROWN

        # --- DRAWING BY VIEW ---
        if self.view == "FRONT":
            pygame.draw.rect(surface, active_hair_color, (x + 8, y + bob, 24, 25), border_radius=5)
            if current_mask == "None":
                pygame.draw.rect(surface, SKIN, (x + 10, y + 12 + bob, 20, 15))
                pygame.draw.rect(surface, EYE_BLUE, (x + 12, y + 15 + bob, 4, 6))
                pygame.draw.rect(surface, EYE_BLUE, (x + 24, y + 15 + bob, 4, 6))
            pygame.draw.rect(surface, SHIRT_DARK, (x + 6, y + 35 + bob, 28, 30))
            # Arms & Hands
            pygame.draw.rect(surface, SKIN, (x + 2, y + 35 + bob, 4, 18))
            pygame.draw.rect(surface, SKIN, (x + 34, y + 35 + bob, 4, 18))
            pygame.draw.rect(surface, SKIN, (x + 1, y + 53 + bob, 6, 6))
            pygame.draw.rect(surface, SKIN, (x + 33, y + 53 + bob, 6, 6))
            # Legs & Boots
            pygame.draw.rect(surface, PANTS_BROWN, (x + 8, y + 65, 10, 20 + leg_step))
            pygame.draw.rect(surface, PANTS_BROWN, (x + 22, y + 65, 10, 20 - leg_step))
            pygame.draw.rect(surface, BOOT_COLOR, (x + 7, y + 85 + leg_step, 12, 8), border_radius=2)
            pygame.draw.rect(surface, BOOT_COLOR, (x + 21, y + 85 - leg_step, 12, 8), border_radius=2)

        elif self.view == "BACK":
            pygame.draw.rect(surface, active_hair_color, (x + 8, y + bob, 24, 30))
            pygame.draw.rect(surface, SHIRT_DARK, (x + 6, y + 35 + bob, 28, 30))
            # BACK ARMS & HANDS (Visible behind shirt)
            pygame.draw.rect(surface, SKIN, (x + 3, y + 35 + bob, 4, 18))
            pygame.draw.rect(surface, SKIN, (x + 33, y + 35 + bob, 4, 18))
            pygame.draw.rect(surface, SKIN, (x + 2, y + 53 + bob, 6, 6))
            pygame.draw.rect(surface, SKIN, (x + 32, y + 53 + bob, 6, 6))
            # BACK LEGS & BOOTS (Separated)
            pygame.draw.rect(surface, PANTS_BROWN, (x + 8, y + 65, 10, 20 + leg_step))
            pygame.draw.rect(surface, PANTS_BROWN, (x + 22, y + 65, 10, 20 - leg_step))
            pygame.draw.rect(surface, BOOT_COLOR, (x + 7, y + 85 + leg_step, 12, 8), border_radius=2)
            pygame.draw.rect(surface, BOOT_COLOR, (x + 21, y + 85 - leg_step, 12, 8), border_radius=2)

        elif self.view in ["LEFT", "RIGHT"]:
            is_right = self.view == "RIGHT"
            pygame.draw.rect(surface, active_hair_color, (x + 12, y + bob, 16, 30))
            if current_mask == "None":
                face_x = x + 15 if is_right else x + 10
                pygame.draw.rect(surface, SKIN, (face_x, y + 12 + bob, 10, 15))
                eye_x = face_x + (6 if is_right else 1)
                pygame.draw.rect(surface, EYE_BLUE, (eye_x, y + 15 + bob, 3, 5))
                # Fringe
                f_x = face_x + (9 if is_right else -2)
                pygame.draw.rect(surface, BEARD_BROWN, (f_x, y + 10 + bob, 3, 8))
            
            pygame.draw.rect(surface, SHIRT_DARK, (x + 14, y + 35 + bob, 12, 30))
            # Side arm/hand
            arm_x = x + 24 if is_right else x + 10
            pygame.draw.rect(surface, SKIN, (arm_x, y + 38 + bob, 5, 15))
            pygame.draw.rect(surface, SKIN, (arm_x - 1, y + 53 + bob, 7, 6))
            # Side legs & boot
            pygame.draw.rect(surface, PANTS_BROWN, (x + 14, y + 65, 6, 20 + leg_step))
            pygame.draw.rect(surface, PANTS_BROWN, (x + 20, y + 65, 6, 20 - leg_step))
            pygame.draw.rect(surface, BOOT_COLOR, (x + 14, y + 85 + leg_step, 12, 8))

        if current_mask != "None":
            self.draw_mask_head(surface, x + 20, y + bob + 5, current_mask, self.view)

# --- MAIN LOOP ---
p = Player(WIDTH//2, HEIGHT//2)
while True:
    screen.fill((230, 230, 230))
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: p.mask_index = 1
            if event.key == pygame.K_2: p.mask_index = 2
            if event.key == pygame.K_3: p.mask_index = 3
            if event.key == pygame.K_0: p.mask_index = 0 
    p.move(); p.draw(screen)
    pygame.display.flip(); clock.tick(60)