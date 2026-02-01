import argparse
import math
import os
import pygame
import sys
import time

pygame.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 800, 600
FPS = 60
SCENE_DURATION = 5  # seconds per scene (~40s total)

screen = None
clock = None
font = None

# Recording helpers
try:
    import imageio
    HAVE_IMAGEIO = True
except Exception:
    HAVE_IMAGEIO = False

BASE_DIR = os.path.dirname(__file__)
RECORD_FILE = None
WRITER = None
FRAMES_DIR = None
FRAME_COUNT = 0

# ---------------- IMAGE LOADER ----------------
def load_img(path, size=None):
    full = path if os.path.isabs(path) else os.path.join(BASE_DIR, path)
    if not os.path.exists(full):
        surf = pygame.Surface(size if size else (100, 100))
        surf.fill((40, 40, 40))
        return surf

    img = pygame.image.load(full).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

# ---------------- STORY SCENES ----------------
scene_defs = [
    {"bg": "assests_story/temple_bg.jpeg", "img": None,
     "text": "When the last temple fell silent, the land forgot its gods."},

    {"bg": "assests_story/forest_pix_ui.jpeg", "img": "assests_story/ghost.png",
     "text": "From broken rituals, ghosts returned to claim the night."},

    {"bg": "assests_story/forest_pix_ui.jpeg", "img": "assests_story/theyyam_pix_ui.png",
     "text": "Theyyam commands fire itself, but the flames slow his steps."},

    {"bg": "assests_story/forest_pix_ui.jpeg", "img": "assests_story/garuda.png",
     "text": "Garudan moves faster than fear, yet a ghost’s touch freezes him."},

    {"bg": "assests_story/forest_pix_ui.jpeg", "img": "assests_story/kali.png",
     "text": "Kali kills with one strike, but darkness steals her sight."},

    {"bg": "assests_story/forest_pix_ui.jpeg", "img": "assests_story/ghost.png",
     "text": "Power was sealed, for every mask carried a deadly curse."},

    {"bg": "assests_story/forest_pix_ui.jpeg", "img": None,
     "text": "Now the masks awaken once more… seeking a bearer."},

    {"bg": "assests_story/forest_pix_ui.jpeg", "img": None,
     "text": "Wear the mask. Endure the curse. Survive the night."},
]

def load_scene_assets():
    scenes = []
    for s in scene_defs:
        bg = load_img(s["bg"], (WIDTH, HEIGHT))
        img = load_img(s["img"]) if s["img"] else None
        scenes.append({"bg": bg, "img": img, "text": s["text"]})
    return scenes

# ---------------- UI HELPERS ----------------
def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines, current = [], ""
    for w in words:
        test = current + w + " "
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = w + " "
    lines.append(current)
    return lines

def draw_dialog_box(text):
    box = pygame.Surface((WIDTH, 140))
    box.set_alpha(200)
    box.fill((0, 0, 0))
    screen.blit(box, (0, HEIGHT - 140))

    y = HEIGHT - 110
    for line in wrap_text(text, font, WIDTH - 80):
        txt = font.render(line, True, (230, 230, 230))
        screen.blit(txt, (40, y))
        y += 28

# ---------------- RECORD FRAME ----------------
def capture_frame():
    global FRAME_COUNT
    if not RECORD_FILE:
        return
    arr = pygame.surfarray.array3d(screen).swapaxes(0, 1)
    if HAVE_IMAGEIO and WRITER:
        WRITER.append_data(arr)
    else:
        pygame.image.save(screen, f"{FRAMES_DIR}/frame_{FRAME_COUNT:06d}.png")
        FRAME_COUNT += 1

# ---------------- INTRO SCREENS ----------------
def show_powered_by_banner(seconds=2):
    title_font = pygame.font.Font(None, 36)
    team_font = pygame.font.Font(None, 56)
    start = time.time()

    while time.time() - start < seconds:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        t1 = title_font.render("powered by", True, (200, 200, 200))
        t2 = team_font.render("TEAM VECTRA", True, (255, 255, 255))

        screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 60))
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2))

        pygame.display.update()
        capture_frame()
        clock.tick(FPS)

def show_logo_animation(logo_img, seconds=2.5):
    start = time.time()
    while time.time() - start < seconds:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        pulse = 1 + 0.05 * math.sin((time.time() - start) * 6)
        w = int(logo_img.get_width() * pulse)
        h = int(logo_img.get_height() * pulse)

        logo = pygame.transform.smoothscale(logo_img, (w, h))
        screen.blit(logo, (WIDTH//2 - w//2, HEIGHT//2 - h//2))

        pygame.display.update()
        capture_frame()
        clock.tick(FPS)

def fade_in():
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill((0, 0, 0))
    for a in range(255, -1, -8):
        fade.set_alpha(a)
        screen.blit(fade, (0, 0))
        pygame.display.update()
        capture_frame()
        clock.tick(FPS)

# ---------------- MAIN STORY ----------------
def run_story(record_file=None):
    global screen, clock, font, RECORD_FILE, WRITER, FRAMES_DIR

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mukha Tejah – Story")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)

    RECORD_FILE = record_file
    if RECORD_FILE and HAVE_IMAGEIO:
        WRITER = imageio.get_writer(RECORD_FILE, fps=FPS)

    scenes = load_scene_assets()

    # Load VECTRA/logo image robustly (check title_heading_ui then assests_ui)
    def find_logo_path():
        # 1) check title_heading_ui folder
        th_dir = os.path.join(BASE_DIR, "assests_ui", "title_heading_ui")
        if os.path.isdir(th_dir):
            for f in os.listdir(th_dir):
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return os.path.join("assests_ui", "title_heading_ui", f)
        # 2) search top-level assests_ui for a file containing 'logo' or 'vectra'
        ui_dir = os.path.join(BASE_DIR, "assests_ui")
        if os.path.isdir(ui_dir):
            for f in os.listdir(ui_dir):
                if f.lower().endswith(('.png', '.jpg', '.jpeg')) and (
                    'logo' in f.lower() or 'vectra' in f.lower()
                ):
                    return os.path.join("assests_ui", f)
        return None

    logo_path = find_logo_path()
    logo_img = None
    if logo_path:
        logo_img = load_img(logo_path)
        # ensure logo has valid size and scale to ~40% width
        if logo_img and logo_img.get_width() > 0:
            max_w = int(WIDTH * 0.4)
            lw = min(max_w, logo_img.get_width())
            lh = int(lw * logo_img.get_height() / logo_img.get_width()) if logo_img.get_width() else lw
            try:
                logo_img = pygame.transform.smoothscale(logo_img, (lw, lh))
            except Exception:
                # keep original if scaling fails
                pass

    # ---- INTRO ----
    show_powered_by_banner()
    if logo_img:
        show_logo_animation(logo_img)
    fade_in()

    # ---- STORY LOOP ----
    idx = 0
    start = time.time()
    running = True

    while running:
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_ESCAPE):
                idx += 1
                start = time.time()
                fade_in()

        if time.time() - start > SCENE_DURATION:
            idx += 1
            start = time.time()
            fade_in()

        if idx >= len(scenes):
            break

        scene = scenes[idx]
        screen.blit(scene["bg"], (0, 0))

        if scene["img"]:
            bob = int(math.sin((time.time() - start) * 2) * 10)
            r = scene["img"].get_rect(center=(WIDTH//2, HEIGHT//2 - 80 + bob))
            screen.blit(scene["img"], r)

        draw_dialog_box(scene["text"])
        pygame.display.update()
        capture_frame()

    if WRITER:
        WRITER.close()

    pygame.quit()

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", help="Output mp4 filename")
    args = parser.parse_args()
    run_story(args.record)
