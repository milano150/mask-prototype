import pygame

# -------------------------
# CHANNELS (created after init)
# -------------------------
FOOTSTEP_CHANNEL = None
SFX_CHANNEL = None
WEAPON_CHANNEL = None

# -------------------------
# SOUNDS (loaded later)
# -------------------------
click = None
footstep = None
sword_swing = None
freeze = None
fireball_sound = None


def load_sounds():
    global click, footstep, sword_swing, freeze, fireball_sound
    global FOOTSTEP_CHANNEL, SFX_CHANNEL, WEAPON_CHANNEL

    FOOTSTEP_CHANNEL = pygame.mixer.Channel(1)
    SFX_CHANNEL = pygame.mixer.Channel(2)
    WEAPON_CHANNEL = pygame.mixer.Channel(3)

    click = pygame.mixer.Sound("assets/sounds/mouse_click_audio.wav")
    footstep = pygame.mixer.Sound("assets/sounds/footsteps.mp3")
    sword_swing = pygame.mixer.Sound("assets/sounds/sword_atk_2.wav")
    freeze = pygame.mixer.Sound("assets/sounds/player_freeze.wav")
    fireball_sound = pygame.mixer.Sound("assets/sounds/fire_sound_effect.wav")

    click.set_volume(0.4)
    footstep.set_volume(0.12)
    sword_swing.set_volume(0.25)
    freeze.set_volume(0.08)
    fireball_sound.set_volume(0.25)
