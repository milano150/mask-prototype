import pygame

pygame.mixer.init()

# -------------------------
# LOAD SOUNDS
# -------------------------
click = pygame.mixer.Sound("assets/sounds/mouse_click_audio.wav")
footstep = pygame.mixer.Sound("assets/sounds/footsteps.mp3")
FOOTSTEP_CHANNEL = pygame.mixer.Channel(1)
sword_swing = pygame.mixer.Sound("assets/sounds/sword_atk_2.wav")
freeze = pygame.mixer.Sound("assets/sounds/player_freeze.wav")



# -------------------------
# VOLUMES
# -------------------------
click.set_volume(0.4)
footstep.set_volume(0.1)
sword_swing.set_volume(0.2)
freeze.set_volume(0.05)

