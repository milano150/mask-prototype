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

# Screen/clock/font will be provided when the story is run inside a game or will be created when run standalone.
screen = None
clock = None
font = None

# Recording / helper flags
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

# ---------------- LOAD IMAGES ----------------
def load_img(path, size=None):
    """Load an image and return a scaled surface. If file missing, return a placeholder surface."""
    full = path if os.path.isabs(path) else os.path.join(BASE_DIR, path)
    if not os.path.exists(full):
        print(f"Warning: image not found: {path}")
        # create placeholder surface
        w, h = size if size else (100, 100)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((40, 40, 40))
        try:
            warn_font = pygame.font.Font(None, 20)
            txt = warn_font.render("Missing: " + os.path.basename(path), True, (255, 60, 60))
            surf.blit(txt, (8, 8))
        except Exception:
            pass
        return surf

    img = pygame.image.load(full).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

# Scene definitions: paths are resolved and loaded when `run_story` is called (safer for importing from the main game)
scene_defs = [
    {"bg": "assests_story/temple_bg.jpeg", "img": None, "text": "When the last temple fell silent, the land forgot its gods."},
    {"bg": "assests_story/forest_pix_ui.jpeg", "img": "assests_story/ghost.png", "text": "From broken rituals, ghosts returned to claim the night."},
    {"bg": "assests_story/forest_pix_ui.jpeg", "img": "assests_story/theyyam_pix_ui.png", "text": "Theyyam commands fire itself, but the flames slow his steps."},
    {"bg": "assests_story/forest_pix_ui.jpeg", "img": "assests_story/garuda.png", "text": "Garudan moves faster than fear, yet a ghost’s touch freezes him."},
    {"bg": "assests_story/forest_pix_ui.jpeg", "img": "assests_story/kali.png", "text": "Kali kills with one strike, but darkness steals her sight."},
    {"bg": "assests_story/forest_pix_ui.jpeg", "img": "assests_story/ghost.png", "text": "Power was sealed, for every mask carried a deadly curse."},
    {"bg": "assests_story/forest_pix_ui.jpeg", "img": None, "text": "Now the masks awaken once more… seeking a bearer."},
    {"bg": "assests_story/forest_pix_ui.jpeg", "img": None, "text": "Wear the mask. Endure the curse. Survive the night."},
]


def load_scene_assets(width, height):
    """Load surfaces for all scene definitions and return scenes list.
    This ensures pygame is initialized before we attempt to load images or create fonts.
    """
    scenes = []
    for sd in scene_defs:
        bg = load_img(sd["bg"], (width, height))
        img = load_img(sd["img"]) if sd["img"] else None
        scenes.append({"bg": bg, "img": img, "text": sd["text"]})
    return scenes

# ---------------- DIALOG BOX ----------------
def draw_dialog_box(text):
    box_height = 140
    box = pygame.Surface((WIDTH, box_height))
    box.set_alpha(200)
    box.fill((0, 0, 0))
    screen.blit(box, (0, HEIGHT - box_height))

    wrapped = wrap_text(text, font, WIDTH - 80)
    y = HEIGHT - box_height + 30
    for line in wrapped:
        render = font.render(line, True, (230, 230, 230))
        screen.blit(render, (40, y))
        y += 28

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""

    for word in words:
        test = current + word + " "
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = word + " "
    lines.append(current)
    return lines

# ---------------- FADE IN ----------------

def run_story(screen_arg=None, clock_arg=None, record_file=None, width=WIDTH, height=HEIGHT, fps=FPS, scene_duration=SCENE_DURATION):
    """Run the story. If `screen_arg` and `clock_arg` are provided, use them (allow embedding inside an existing pygame app).
    If not provided, create a temporary display and quit it when finished.
    Returns when story completes or when user quits.
    """
    global screen, clock, font, RECORD_FILE, WRITER, FRAMES_DIR, FRAME_COUNT

    created_display = False

    # Setup display/clock/font
    if screen_arg is None:
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Mukha Tejah - Story")
        created_display = True
    else:
        screen = screen_arg

    clock = clock_arg if clock_arg is not None else pygame.time.Clock()
    if font is None:
        font = pygame.font.Font(None, 30)

    # Recording setup
    RECORD_FILE = record_file
    WRITER = None
    FRAMES_DIR = None
    FRAME_COUNT = 0
    if RECORD_FILE:
        if HAVE_IMAGEIO:
            WRITER = imageio.get_writer(RECORD_FILE, fps=fps)
            print(f"Recording enabled — writing to: {RECORD_FILE}")
        else:
            FRAMES_DIR = os.path.join(BASE_DIR, "story_frames")
            os.makedirs(FRAMES_DIR, exist_ok=True)
            FRAME_COUNT = 0
            print(f"imageio not available — saving frames to: {FRAMES_DIR}")

    # Load assets now that pygame is initialized
    scenes = load_scene_assets(width, height)

    def capture_frame():
        """Save or append the current screen to the writer or frames dir (if recording)."""
        global FRAME_COUNT
        if not RECORD_FILE:
            return
        try:
            arr = pygame.surfarray.array3d(screen).swapaxes(0, 1)
            if HAVE_IMAGEIO and WRITER:
                WRITER.append_data(arr)
            else:
                fname = os.path.join(FRAMES_DIR, f"frame_{FRAME_COUNT:06d}.png")
                pygame.image.save(screen, fname)
                FRAME_COUNT += 1
        except Exception as e:
            print("Warning: failed to capture frame:", e)

    def fade_in():
        fade = pygame.Surface((width, height))
        fade.fill((0, 0, 0))
        for alpha in range(255, -1, -8):
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    if WRITER:
                        WRITER.close()
                    if created_display:
                        pygame.quit()
                    sys.exit()
            fade.set_alpha(alpha)
            screen.blit(fade, (0, 0))
            pygame.display.update()
            capture_frame()
            clock.tick(fps)

    # Story loop
    scene_index = 0
    scene_start = time.time()

    fade_in()

    running = True
    while running:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if WRITER:
                    WRITER.close()
                if created_display:
                    pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if WRITER:
                        WRITER.close()
                    if created_display:
                        pygame.quit()
                    return
                elif event.key in (pygame.K_SPACE, pygame.K_RIGHT):
                    # manual skip to next scene
                    scene_index += 1
                    scene_start = time.time()
                    fade_in()
                    if scene_index >= len(scenes):
                        running = False
                        break

        # Auto scene switch
        if time.time() - scene_start > scene_duration:
            scene_index += 1
            scene_start = time.time()
            fade_in()

            if scene_index >= len(scenes):
                running = False
                break

        scene = scenes[scene_index]

        # Draw background
        screen.blit(scene["bg"], (0, 0))

        # Draw image (simple bobbing animation)
        if scene["img"]:
            bob = int(math.sin((time.time() - scene_start) * 2.0) * 10)
            img = scene["img"]
            rect = img.get_rect(center=(width // 2, height // 2 - 80 + bob))
            screen.blit(img, rect)

        # Draw dialog
        draw_dialog_box(scene["text"])

        pygame.display.update()
        capture_frame()

    # ---------------- TRANSITION TO GAME ----------------
    # Try to show a poster image (any file with 'poster' in its name inside assests_story),
    # otherwise fall back to the forest background. Show it expanded to fill the screen.
    poster_path = None
    try:
        story_dir = os.path.join(BASE_DIR, "assests_story")
        for fname in os.listdir(story_dir):
            if "poster" in fname.lower():
                poster_path = os.path.join("assests_story", fname)
                break
    except Exception:
        poster_path = None

    if not poster_path:
        poster_path = "assests_story/forest_pix_ui.jpeg"

    poster = load_img(poster_path, (width, height))

    # show poster for a short duration, capturing frames if recording
    show_seconds = 3
    end_time = time.time() + show_seconds
    while time.time() < end_time:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                if WRITER:
                    WRITER.close()
                if created_display:
                    pygame.quit()
                return
        screen.blit(poster, (0, 0))
        pygame.display.update()
        capture_frame()
        clock.tick(fps)

    # Close any writer if recording
    if WRITER:
        try:
            WRITER.close()
            print(f"Saved video: {RECORD_FILE}")
        except Exception as e:
            print("Warning: failed to close writer:", e)
    elif RECORD_FILE:
        # frames were saved to disk
        print(f"Frames saved to {FRAMES_DIR}. To assemble into mp4, run: \nffmpeg -r {fps} -i {os.path.join(FRAMES_DIR, 'frame_%06d.png')} -c:v libx264 -pix_fmt yuv420p {RECORD_FILE}")

    if created_display:
        pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run story and optionally record to a video")
    parser.add_argument("--record", help="Output mp4 filename (example: --record story.mp4)")
    args = parser.parse_args()

    run_story(record_file=args.record)

