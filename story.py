import argparse
import math
import os
import pygame
import sys
import time

pygame.init()
pygame.mixer.init()

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
def run_story(record_file=None, music_file=None):
    global screen, clock, font, RECORD_FILE, WRITER, FRAMES_DIR

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mukha Tejah – Story")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)

    RECORD_FILE = record_file
    if RECORD_FILE and HAVE_IMAGEIO:
        WRITER = imageio.get_writer(RECORD_FILE, fps=FPS)

    scenes = load_scene_assets()
        # ---------------- BACKGROUND MUSIC ----------------
    def find_music_path():
        # preferred: assests_ui/sound_ui/background_music.*
        candidates = [
            os.path.join(BASE_DIR, "assests_ui", "sound_ui"),
            os.path.join(BASE_DIR, "assests_ui"),
            os.path.join(BASE_DIR, "assests_story"),
            os.path.join(BASE_DIR, "assets"),
        ]
        exts = (".mp3", ".ogg", ".wav", ".m4a", ".flac")
        # check specific filename first
        specific = os.path.join(BASE_DIR, "assests_ui", "sound_ui", "background_music.mp3")
        if os.path.exists(specific):
            return specific
        # search candidates for first file matching extension
        for d in candidates:
            try:
                if not os.path.isdir(d):
                    continue
                for f in os.listdir(d):
                    if f.lower().endswith(exts):
                        return os.path.join(d, f)
            except Exception:
                continue
        return None

    music_path = find_music_path()
    music_loaded = False

    if music_path:
        try:
            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init()
                except Exception as e:
                    print("Warning: pygame.mixer failed to init:", e)
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.7)
            music_loaded = True
            print(f"Background music loaded: {music_path}")
        except Exception as e:
            print("Failed to load background music:", e)
    else:
        # No music file found — generate a simple test tone and use that so the story has background audio.
        try:
            gen_dir = os.path.join(BASE_DIR, "assests_ui", "sound_ui")
            os.makedirs(gen_dir, exist_ok=True)
            gen_path = os.path.join(gen_dir, "background_music.wav")

            # generate a simple wav (sine wave) if it does not exist
            if not os.path.exists(gen_path):
                import wave, struct
                duration = 6.0
                framerate = 44100
                amplitude = 16000
                freq1 = 220.0
                freq2 = 330.0
                nframes = int(duration * framerate)
                with wave.open(gen_path, 'w') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(framerate)
                    for i in range(nframes):
                        t = float(i) / framerate
                        # simple two-tone mix
                        val = int(amplitude * (0.5 * (math.sin(2.0 * math.pi * freq1 * t) + math.sin(2.0 * math.pi * freq2 * t))))
                        data = struct.pack('<h', max(-32767, min(32767, val)))
                        wf.writeframesraw(data)
                print(f"Generated test music at: {gen_path}")
            music_path = gen_path
            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init()
                except Exception as e:
                    print("Warning: pygame.mixer failed to init:", e)
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.7)
            music_loaded = True
            print("Using generated test background music.")
        except Exception as e:
            print("Could not generate test music:", e)
            print("No background music will be played. To use your own music pass --music <path> or add files to assests_ui/sound_ui.")
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
                # ---- MUSIC CONTROL (Slide 3 to Slide 8) ----
        if music_loaded:
            # Start music at slide index 2 (Slide 3)
            if idx == 2 and not pygame.mixer.music.get_busy():
                try:
                    pygame.mixer.music.play(-1)
                    print("Background music started")
                except Exception as e:
                    print("Failed to start background music:", e)

            # Stop music after slide index 7 (Slide 8)
            if idx > 7 and pygame.mixer.music.get_busy():
                try:
                    pygame.mixer.music.stop()
                    print("Background music stopped")
                except Exception as e:
                    print("Failed to stop background music:", e)

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
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    pygame.quit()

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", help="Output mp4 filename")
    parser.add_argument("--music", help="Path to background music file to use (overrides discovery)")
    args = parser.parse_args()
    run_story(args.record, music_file=args.music)