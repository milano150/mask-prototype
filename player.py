import pygame
import math
import random
from fireball import Fireball

# =====================
# HEALTH BAR CONSTANTS
# =====================
BAR_WIDTH = 64
BAR_HEIGHT = 64
TOTAL_FRAMES = 13
COLUMNS = 3



class HealthBar:
    def __init__(self, max_health):
        self.max_health = max_health
        self.step = max_health / TOTAL_FRAMES
        self.current_step = 0

    def take_damage(self, amount):
        steps_lost = round(amount / self.step)
        self.current_step = min(
            TOTAL_FRAMES - 1,
            self.current_step + max(1, steps_lost)
        )

    def heal(self, amount):
        steps_gained = round(amount / self.step)
        self.current_step = max(
            0,
            self.current_step - max(1, steps_gained)
        )

    def get_frame_rect(self):
        frame_index = self.current_step
        col = frame_index % COLUMNS
        row = frame_index // COLUMNS
        return pygame.Rect(
            col * BAR_WIDTH,
            row * BAR_HEIGHT,
            BAR_WIDTH,
            BAR_HEIGHT
        )


# =====================
# COLORS
# =====================
SKIN = (255, 180, 130)
BEARD_BROWN = (60, 30, 10)
SHIRT_DARK = (40, 40, 40)
PANTS_BROWN = (100, 50, 20)
EYE_BLUE = (10, 10, 10)
BOOT_COLOR = (45, 30, 20)
DUST_COLOR = (200, 200, 200)
GOLD, RED, BLUE, YELLOW = (218, 165, 32), (200, 0, 0), (30, 60, 180), (255, 215, 0)


# =====================
# DUST PARTICLE
# =====================
class Dust:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.size = random.randint(2, 4)
        self.life = 25
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-0.5, -1)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface, camera_offset):
        if self.life > 0:
            cx, cy = camera_offset
            pygame.draw.circle(
                surface, DUST_COLOR,
                (int(self.x - cx), int(self.y - cy)),
                self.size
            )



# =====================
# PLAYER
# =====================
class Player:
    def __init__(self, x, y):
        self.dead = False
        self.rect = pygame.Rect(0, 0, 40, 105)
        self.rect.center = (x, y)


        self.masks = {
            "theyyam": {"speed": 400},
            "garuda": {"speed": 700},
            "kali": {"speed": 400},
        }

        self.mask_switch_cd = 0.0
        self.mask_switch_delay = 1.2  # seconds




        self.current_mask = "theyyam"
        self.speed = self.masks[self.current_mask]["speed"]

        self.health_bar = HealthBar(100)

        # --- Fireball cooldown (Theyyam) ---
        self.fireball_cooldown = 0.8  # seconds
        self.fireball_timer = 0.0


        # Movement / view
        self.facing = 1          # 1 = right, -1 = left
        self.view = "FRONT"
        self.walk_count = 0
        self.dust_particles = []

        # Sword combat stats
        self.sword_damage = 25
        self.attack_cooldown = 400  # ms
        self.last_attack = 0


        # Sword (Kali)
        self.sword_img = pygame.image.load("assets/sword.png").convert_alpha()
        self.sword_img = pygame.transform.scale(
            self.sword_img,
            (self.sword_img.get_width() * 3,
             self.sword_img.get_height() * 3)
        )
        self.sword_img = pygame.transform.rotate(self.sword_img, -90)
        self.sword_angle = 0
        self.sword_swinging = False
        self.sword_timer = 0
        self.sword_duration = 12

        # --- physics / knockback (velocity-based, decays over time) ---
        # vx/vy: knockback velocity in pixels/second applied on top of player input
        self.vx = 0.0
        self.vy = 0.0
        self.knockback_resistance = 1.0   # higher -> less effect
        self.max_knockback_speed = 800.0  # px/s cap for impulses
        self.knockback_friction = 4.5    # decay rate (per second)
        self.knockback_timer = 0.0        # seconds of reduced control
        self.knockback_stun = 0.15
        self.invul_timer = 0.0
        self.invul_time = 0.25

        self.move_vx = 0.0
        self.move_vy = 0.0
        self.move_accel = 15000.0   # how fast you speed up
        self.move_drag = 10.0     # how fast you slow down

    # -----------------
    # MASK
    # -----------------
    def change_mask(self, mask_name):
        if mask_name in self.masks:
            self.current_mask = mask_name
            self.speed = self.masks[mask_name]["speed"]
    def respawn(self, x, y):
        self.rect.center = (x, y)
        self.health_bar = HealthBar(100)
        self.dead = False

        self.vx = 0
        self.vy = 0
        self.move_vx = 0
        self.move_vy = 0

        self.sword_swinging = False
        self.fireball_timer = 0



    # -----------------
    # COMBAT
    # -----------------
    def shoot_fireball(self):
        if self.current_mask != "theyyam":
            return None

        if self.fireball_timer > 0:
            return None

        fx = self.rect.centerx
        fy = self.rect.centery

        fireball = Fireball(fx, fy, self.facing)

        self.fireball_timer = self.fireball_cooldown
        return fireball   # ✅ IMPORTANT


    def take_damage(self, amount):
        self.health_bar.take_damage(amount)
        if self.health_bar.current_step >= TOTAL_FRAMES - 1:
            self.dead = True
    def sword_attack(self, ghosts, debug_surface=None):
        now = pygame.time.get_ticks()
        if now - self.last_attack < self.attack_cooldown:
            return

        self.last_attack = now

        # Bigger, centered sword hitbox
        hitbox = pygame.Rect(
            self.rect.right if self.facing == 1 else self.rect.left - 40,
            self.rect.centery - 25,
            40,
            50
        )

        # 🔍 DEBUG DRAW (only if surface is passed)
        if debug_surface:
            pygame.draw.rect(debug_surface, (255, 0, 0), hitbox, 2)

        for ghost in ghosts:
            if ghost.alive and hitbox.colliderect(ghost.rect):
                ghost.take_damage(self.sword_damage)

                ghost.apply_knockback(
                    self.rect.centerx,
                    self.rect.centery,
                    16
                )


    # -----------------
    # UPDATE
    # -----------------
    def update(self, keys, dt):
        if self.dead:
            return

        dx = dy = 0
        moving = False

        if keys[pygame.K_a]:
            dx -= 1.5
            self.facing = -1
            self.view = "LEFT"
            moving = True
        if keys[pygame.K_d]:
            dx += 1.5
            self.facing = 1
            self.view = "RIGHT"
            moving = True
        if keys[pygame.K_w]:
            dy -= 1.5
            self.view = "BACK"
            moving = True
        if keys[pygame.K_s]:
            dy += 1.5
            self.view = "FRONT"
            moving = True

        if moving:
            self.walk_count += dt * 10
        else:
            self.walk_count = 0


        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length

        # while knocked back the player has reduced control
        control_mul = 0.3 if self.knockback_timer > 0 else 1.0

        # target velocity from input
        target_vx = dx * self.speed * control_mul
        target_vy = dy * self.speed * control_mul

        # accelerate towards target velocity
        self.move_vx += (target_vx - self.move_vx) * self.move_accel * dt / self.speed
        self.move_vy += (target_vy - self.move_vy) * self.move_accel * dt / self.speed

        # apply drag when no input
        self.move_vx *= max(0.0, 1.0 - self.move_drag * dt)
        self.move_vy *= max(0.0, 1.0 - self.move_drag * dt)

        # apply movement + knockback velocity
        self.rect.x += (self.move_vx + self.vx) * dt
        self.rect.y += (self.move_vy + self.vy) * dt



        # decay knockback velocity (simple exponential-like decay)
        self.vx *= max(0.0, 1.0 - self.knockback_friction * dt)
        self.vy *= max(0.0, 1.0 - self.knockback_friction * dt)
        # snap small velocities to zero to avoid jitter
        if abs(self.vx) < 5:
            self.vx = 0.0
        if abs(self.vy) < 5:
            self.vy = 0.0

        # timers (seconds)
        if self.knockback_timer > 0:
            self.knockback_timer = max(0.0, self.knockback_timer - dt)
        if self.invul_timer > 0:
            self.invul_timer = max(0.0, self.invul_timer - dt)
        if moving and random.random() > 0.85:
            self.dust_particles.append(
                Dust(self.rect.centerx, self.rect.bottom - 5)
            )

        else:
            self.walk_count = 0

        for d in self.dust_particles[:]:
            d.update()
            if d.life <= 0:
                self.dust_particles.remove(d)
        # Fireball cooldown countdown
        if self.fireball_timer > 0:
            self.fireball_timer -= dt
            if self.fireball_timer < 0:
                self.fireball_timer = 0





        # Sword animation
        if self.sword_swinging:
            self.sword_timer -= 1


            
            if self.facing == 1:
                self.sword_angle -= 6
            else:
                self.sword_angle += 6

            if self.sword_timer <= 0:
                self.sword_swinging = False
                self.sword_angle = 0
        if self.mask_switch_cd > 0:
            self.mask_switch_cd -= dt
            self.mask_switch_cd = max(0, self.mask_switch_cd)


    # -----------------
    # MASK HEAD
    # -----------------
    def draw_mask_head(self, surface, x, y, view):
        mx, my = x, y + 5

        if self.current_mask == "theyyam":
            base_c, face_c = GOLD, RED
        elif self.current_mask == "garuda":
            base_c, face_c = RED, YELLOW
        else:  # kali
            base_c, face_c = (192, 192, 192), BLUE

        if view == "FRONT":
            pygame.draw.circle(surface, base_c, (mx, my), 15)
            pygame.draw.rect(surface, face_c, (mx - 15, my - 12, 30, 35), border_radius=2)
            pygame.draw.circle(surface, (10, 10, 10), (mx - 7, my + 2), 4)
            pygame.draw.circle(surface, (10, 10, 10), (mx + 7, my + 2), 4)

        elif view == "BACK":
            pygame.draw.circle(surface, base_c, (mx, my), 12)
            pygame.draw.rect(surface, face_c, (mx - 12, my - 5, 24, 28), border_radius=2)

        else:  # SIDE
            is_right = (view == "RIGHT")
            side_x = mx + 2 if is_right else mx - 12
            pygame.draw.rect(
                surface,
                base_c,
                (mx + (10 if is_right else -14), my - 20, 4, 15),
                border_radius=1
            )
            pygame.draw.rect(surface, face_c, (side_x, my - 12, 10, 32), border_radius=2)
            eye_x = mx + 6 if is_right else mx - 8
            pygame.draw.circle(surface, (10, 10, 10), (eye_x, my + 2), 3)

    def apply_knockback(self, source_x, source_y, force, stun_time=None, override=False):
        """Apply an impulse away from (source_x, source_y).
        - force: matches previous magnitude (pixels) and is converted to an initial velocity impulse
        - stun_time: seconds of reduced control; if None uses default
        - override: replace existing knockback_timer when True
        """
        if stun_time is None:
            stun_time = self.knockback_stun

        # direction from source -> player
        dx = self.rect.centerx - source_x
        dy = self.rect.centery - source_y
        dist = math.hypot(dx, dy) or 1.0
        nx, ny = dx / dist, dy / dist

        impulse = force / max(0.1, self.knockback_resistance)
        # apply impulse to velocity (px/s)
        self.vx += nx * impulse
        self.vy += ny * impulse * 0.9

        # cap overall knockback speed
        sp = math.hypot(self.vx, self.vy)
        if sp > self.max_knockback_speed:
            s = self.max_knockback_speed / sp
            self.vx *= s
            self.vy *= s

        # timers
        self.knockback_timer = max(self.knockback_timer, stun_time) if not override else stun_time
        self.invul_timer = self.invul_time

    def is_invulnerable(self):
        return self.invul_timer > 0

    def get_rect(self):
        return self.rect


    # -----------------
    # DRAW
    # -----------------
    def draw(self, screen, camera_offset=(0, 0)):
        x, y = self.rect.x, self.rect.y
        bob = math.sin(self.walk_count) * 3
        leg_step = math.sin(self.walk_count) * 6

        cx, cy = camera_offset
        x = self.rect.x - cx
        y = self.rect.y - cy

        for d in self.dust_particles:
            d.draw(screen, (cx, cy))

        # --- BODY ---
        if self.view == "FRONT":
            pygame.draw.rect(screen, BEARD_BROWN, (x + 8, y + bob, 24, 25), border_radius=5)
            pygame.draw.rect(screen, SHIRT_DARK, (x + 6, y + 35 + bob, 28, 30))

            pygame.draw.rect(screen, SKIN, (x + 2, y + 35 + bob, 4, 18))
            pygame.draw.rect(screen, SKIN, (x + 34, y + 35 + bob, 4, 18))
            pygame.draw.rect(screen, SKIN, (x + 1, y + 53 + bob, 6, 6))
            pygame.draw.rect(screen, SKIN, (x + 33, y + 53 + bob, 6, 6))

            pygame.draw.rect(screen, PANTS_BROWN, (x + 8, y + 65, 10, 20 + leg_step))
            pygame.draw.rect(screen, PANTS_BROWN, (x + 22, y + 65, 10, 20 - leg_step))
            pygame.draw.rect(screen, BOOT_COLOR, (x + 7, y + 85 + leg_step, 12, 8), border_radius=2)
            pygame.draw.rect(screen, BOOT_COLOR, (x + 21, y + 85 - leg_step, 12, 8), border_radius=2)

        elif self.view == "BACK":
            pygame.draw.rect(screen, BEARD_BROWN, (x + 8, y + bob, 24, 30))
            pygame.draw.rect(screen, SHIRT_DARK, (x + 6, y + 35 + bob, 28, 30))

            pygame.draw.rect(screen, SKIN, (x + 3, y + 35 + bob, 4, 18))
            pygame.draw.rect(screen, SKIN, (x + 33, y + 35 + bob, 4, 18))
            pygame.draw.rect(screen, SKIN, (x + 2, y + 53 + bob, 6, 6))
            pygame.draw.rect(screen, SKIN, (x + 32, y + 53 + bob, 6, 6))

            pygame.draw.rect(screen, PANTS_BROWN, (x + 8, y + 65, 10, 20 + leg_step))
            pygame.draw.rect(screen, PANTS_BROWN, (x + 22, y + 65, 10, 20 - leg_step))
            pygame.draw.rect(screen, BOOT_COLOR, (x + 7, y + 85 + leg_step, 12, 8), border_radius=2)
            pygame.draw.rect(screen, BOOT_COLOR, (x + 21, y + 85 - leg_step, 12, 8), border_radius=2)

        else:  # LEFT / RIGHT
            is_right = self.view == "RIGHT"
            pygame.draw.rect(screen, BEARD_BROWN, (x + 12, y + bob, 16, 30))
            pygame.draw.rect(screen, SHIRT_DARK, (x + 14, y + 35 + bob, 12, 30))

            arm_x = x + 24 if is_right else x + 10
            pygame.draw.rect(screen, SKIN, (arm_x, y + 38 + bob, 5, 15))
            pygame.draw.rect(screen, SKIN, (arm_x - 1, y + 53 + bob, 7, 6))

            pygame.draw.rect(screen, PANTS_BROWN, (x + 14, y + 65, 6, 20 + leg_step))
            pygame.draw.rect(screen, PANTS_BROWN, (x + 20, y + 65, 6, 20 - leg_step))
            pygame.draw.rect(screen, BOOT_COLOR, (x + 14, y + 85 + leg_step, 12, 8))

        # --- MASK ---
        self.draw_mask_head(screen, x + 20, y + bob + 5, self.view)


        # --- SWORD ---
        if self.current_mask == "kali" and self.sword_swinging:
            sword_img = self.sword_img
            if self.facing == -1:
                sword_img = pygame.transform.flip(sword_img, True, False)

            rotated = pygame.transform.rotate(sword_img, self.sword_angle)
            offset_x = 22 if self.facing == 1 else -22
            rect = rotated.get_rect(
                center=(
                    self.rect.centerx + offset_x - cx,
                    self.rect.centery - cy
                )
            )
            screen.blit(rotated, rect)


