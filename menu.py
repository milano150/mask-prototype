import pygame
import sys
import os
import math 
import glob
import main
from audio import click
import story

pygame.init()

# ------------------ SETTINGS ------------------
WIDTH, HEIGHT = 1000, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mukha Tejah : Mask Power System")

CLOCK = pygame.time.Clock()
FPS = 60

# ------------------ PATHS ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Find an assets UI directory robustly: prefer local 'assets_ui' or 'assests_ui',
# but also search the user's home directory (useful if assets live in a different clone or OneDrive folder).
def find_assets_ui():
    # 1) local candidates
    local_candidates = [
        os.path.join(BASE_DIR, "assets_ui"),
        os.path.join(BASE_DIR, "assests_ui"),
    ]
    for p in local_candidates:
        if os.path.isdir(p):
            return p

    # 2) search the user's home directory for any 'assets_ui' or 'assests_ui' folder (recursive, first match)
    try:
        home = os.path.expanduser("~")
        import glob
        patterns = [
            os.path.join(home, "**", "assets_ui"),
            os.path.join(home, "**", "assests_ui"),
        ]
        for pat in patterns:
            matches = glob.glob(pat, recursive=True)
            for m in matches:
                if os.path.isdir(m):
                    return m
    except Exception:
        pass

    # 3) fallback to local 'assets_ui' path (may not exist)
    return os.path.join(BASE_DIR, "assets_ui")

ASSETS_UI = find_assets_ui()
print(f" Using ASSETS_UI directory: {ASSETS_UI}")

# ------------------ COLORS (FOLK LORE THEME) ------------------
AGNI_GOLD = (215, 145, 40)
RAKTA_RED = (125, 30, 35)
ASH_WHITE = (230, 225, 215)
SHADOW    = (10, 10, 15)

# ------------------ LOAD IMAGES ------------------
# Gather all image files in the ASSETS_UI directory
_image_exts = (".png", ".jpg", ".jpeg")
_image_files = []
if os.path.isdir(ASSETS_UI):
    for f in os.listdir(ASSETS_UI):
        if f.lower().endswith(_image_exts):
            _image_files.append(os.path.join(ASSETS_UI, f))

# Helper: try to load an image path safely
def _safe_load(path, alpha=False):
    try:
        if alpha:
            return pygame.image.load(path).convert_alpha()
        return pygame.image.load(path).convert()
    except Exception:
        return None

# Select background: prefer names with 'back' or 'bg' (allow misspelling like 'backgroud'), else pick the first image
background = None
if _image_files:
    # look for good background candidates
    candidates = [p for p in _image_files if any(k in os.path.basename(p).lower() for k in ("back", "bg", "background", "backgroud", "pix"))]
    if not candidates:
        candidates = _image_files
    for c in candidates:
        img = _safe_load(c, alpha=False)
        if img is not None:
            background = img
            print(f"Background image loaded from assets: {os.path.basename(c)}")
            break



if background is not None:
    try:
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except Exception:
        # In case scaling fails, fallback to surface fill
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((10, 10, 20))
else:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((10, 10, 20))

# Select theyyam: prefer filenames containing 'theyyam' else try any image that looks like a character (png pref)
theyyam = None
if _image_files:
    candidates = [p for p in _image_files if "theyyam" in os.path.basename(p).lower()]
    if not candidates:
        # prefer pngs first, then any
        pngs = [p for p in _image_files if p.lower().endswith('.png')]
        candidates = pngs if pngs else _image_files

    for c in candidates:
        img = _safe_load(c, alpha=True)
        if img is not None:
            theyyam = img
            print(f"Theyyam image loaded from assets: {os.path.basename(c)}")
            break

# Final fallback for theyyam
if theyyam is not None:
    try:
        theyyam = pygame.transform.scale(theyyam, (360, 520))
    except Exception:
        # keep as-is if scaling fails
        pass
else:
    theyyam = pygame.Surface((360, 520), pygame.SRCALPHA)
    pygame.draw.rect(theyyam, AGNI_GOLD, theyyam.get_rect(), 4)

# ------------------ FONTS ------------------
# Attempt to load a project-provided 'Kaliuga' display font from
# assests_ui/title_heading_ui. If not found, fall back to system fonts.
ICON_FONT = pygame.font.SysFont("arial", 36, bold=True)
HS_FONT = pygame.font.SysFont("timesnewroman", 22, bold=True)

# ------------------ FONT LOADER (from repo assets) ------------------
TITLE_FONT = None
BTN_FONT = None




# Directories inside assets where we expect fonts
title_font_dir = os.path.join(ASSETS_UI, "title_heading_ui")
sub_font_dir = os.path.join(ASSETS_UI, "sub_title_ui")

# Prefer the bundled 'Vampire Wars.ttf' if present, otherwise fall back to any font in the dirs
title_path = None
vamp_path = os.path.join(title_font_dir, "Vampire Wars.ttf")
if os.path.isfile(vamp_path):
    title_path = vamp_path
else:
    # fallback to any ttf/otf in the title folder
    if os.path.isdir(title_font_dir):
        for f in os.listdir(title_font_dir):
            if f.lower().endswith((".ttf", ".otf")):
                title_path = os.path.join(title_font_dir, f)
                break

# For button/sub fonts prefer sub_title_ui, otherwise reuse title font
sub_path = None
if os.path.isdir(sub_font_dir):
    for f in os.listdir(sub_font_dir):
        if f.lower().endswith((".ttf", ".otf")):
            sub_path = os.path.join(sub_font_dir, f)
            break

try:
    if title_path:
        TITLE_FONT = pygame.font.Font(title_path, 96)
        print(f"Title font loaded from assets: {os.path.basename(title_path)}")
    else:
        TITLE_FONT = pygame.font.SysFont("timesnewroman", 64, bold=True)
        print(" No title font found in assets; using system font.")
        # Diagnostic: show what's in the title font folder (if present)
        if os.path.isdir(title_font_dir):
            try:
                print("DEBUG: title_heading_ui contents:", os.listdir(title_font_dir))
            except Exception as _:
                print("DEBUG: cannot list title_heading_ui")

    if sub_path:
        BTN_FONT = pygame.font.Font(sub_path, 36)
        HS_FONT = pygame.font.Font(sub_path, 22)
        print(f"UI font loaded from assets: {os.path.basename(sub_path)}")
    elif title_path:
        # reuse title font for UI labels if no sub font available
        BTN_FONT = pygame.font.Font(title_path, 36)
        HS_FONT = pygame.font.Font(title_path, 22)
        print(" Using title font for UI labels since no sub-title font was found.")
    else:
        BTN_FONT = pygame.font.SysFont("timesnewroman", 30, bold=True)
        HS_FONT = pygame.font.SysFont("timesnewroman", 22, bold=True)
        print(" No sub-title font found in assets; using system fonts.")
except Exception as e:
    print(" Error loading fonts from assets, falling back to system fonts:", e)
    TITLE_FONT = pygame.font.SysFont("timesnewroman", 64, bold=True)
    BTN_FONT = pygame.font.SysFont("timesnewroman", 30, bold=True)
    HS_FONT = pygame.font.SysFont("timesnewroman", 22, bold=True)

    if sub_path:
        BTN_FONT = pygame.font.Font(sub_path, 36)
        HS_FONT = pygame.font.Font(sub_path, 22)
        print(f" UI fonts loaded from assets: {os.path.basename(sub_path)}")
    else:
        BTN_FONT = pygame.font.SysFont("timesnewroman", 30, bold=True)
        HS_FONT = pygame.font.SysFont("timesnewroman", 22, bold=True)
        print(" No sub-title font found in assets; using system fonts.")
except Exception as e:
    print("Error loading fonts from assets, falling back to system fonts:", e)
    TITLE_FONT = pygame.font.SysFont("timesnewroman", 64, bold=True)
    BTN_FONT = pygame.font.SysFont("timesnewroman", 30, bold=True)
    HS_FONT = pygame.font.SysFont("timesnewroman", 22, bold=True)

# ------------------ HIGH SCORE HELPERS ------------------
def load_high_score():
    path = os.path.join(BASE_DIR, "highscore.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return int(f.read().strip() or 0)
    except Exception:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("0")
        except Exception:
            pass
        return 0
def save_high_score(new_score):
    path = os.path.join(BASE_DIR, "highscore.txt")
    try:
        old = load_high_score()
        if new_score > old:
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(new_score))
    except Exception:
        pass



def show_modal(title, message, duration=1500):
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < duration:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        SCREEN.blit(overlay, (0, 0))

        # Render title + message directly on the dim overlay (no surrounding box)
        t_surf = TITLE_FONT.render(title, True, ASH_WHITE)
        m_surf = BTN_FONT.render(message, True, ASH_WHITE)

        SCREEN.blit(t_surf, (WIDTH // 2 - t_surf.get_width() // 2, HEIGHT // 2 - t_surf.get_height() - 8))
        SCREEN.blit(m_surf, (WIDTH // 2 - m_surf.get_width() // 2, HEIGHT // 2 + 8))

        pygame.display.update()


# ------------------ MENU FIREBALL (local simple) ------------------
class Fireball:
    def __init__(self):
        self.active = False
        self.x = 420
        self.y = HEIGHT // 2
        self.dx = self.dy = 0

    def shoot(self, tx, ty):
        angle = math.atan2(ty - self.y, tx - self.x)
        self.dx = math.cos(angle) * 15
        self.dy = math.sin(angle) * 15
        self.active = True

    def update(self):
        if not self.active:
            return

        self.x += self.dx
        self.y += self.dy

        pygame.draw.circle(SCREEN, AGNI_GOLD, (int(self.x), int(self.y)), 10)
        pygame.draw.circle(SCREEN, (180, 60, 45), (int(self.x), int(self.y)), 16, 2)

        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.active = False
            self.x, self.y = 420, HEIGHT // 2

# ------------------ BUTTON ------------------
class MenuButton:
    def __init__(self, icon, text, y):
        self.rect = pygame.Rect(620, y, 260, 56)
        self.icon = icon
        self.text = text

    def draw(self, hover):
        bg = RAKTA_RED if hover else SHADOW
        pygame.draw.rect(SCREEN, bg, self.rect, border_radius=12)
        # Removed yellow border (AGNI_GOLD stroke) per request; box is dark-only now

        icon = ICON_FONT.render(self.icon, True, AGNI_GOLD)
        label = BTN_FONT.render(self.text, True, ASH_WHITE)

        # Label: render a black shadow slightly offset, then gold text on top
        label_shadow = BTN_FONT.render(self.text, True, SHADOW)
        label = BTN_FONT.render(self.text, True, AGNI_GOLD)

        SCREEN.blit(icon, (self.rect.x + 18, self.rect.y + 13))
        SCREEN.blit(label_shadow, (self.rect.x + 60 + 2, self.rect.y + 15 + 2))
        SCREEN.blit(label, (self.rect.x + 60, self.rect.y + 15))

# ------------------ TITLE ------------------
def draw_title():
    title = "MUKHA TEJAH"

    shadow = TITLE_FONT.render(title, True, SHADOW)
    main = TITLE_FONT.render(title, True, AGNI_GOLD)

    x = WIDTH // 2 - main.get_width() // 2
    y = 20

    # Black shadow behind gold title
    SCREEN.blit(shadow, (x + 4, y + 4))
    SCREEN.blit(main, (x, y))

# ------------------ MAIN MENU ------------------
def main_menu():
    fireball = Fireball()

    buttons = [
        MenuButton("▶", "NEW GAME", 230),
        MenuButton("📖", "STORY", 300),
        MenuButton("★", "HIGH SCORE", 370),
    ]

    exit_anim = False

    
    while True:
        CLOCK.tick(FPS)
        mouse = pygame.mouse.get_pos()

        highscore = load_high_score()

        # Background
        SCREEN.blit(background, (0, 0))

        # Dark cinematic overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        SCREEN.blit(overlay, (0, 0))

        # Theyyam (LEFT aligned)
        SCREEN.blit(theyyam, (40, 60))

        # Title
        draw_title()

        # Buttons + fireball interaction
        for btn in buttons:
            hover = btn.rect.collidepoint(mouse)
            btn.draw(hover)

            

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].rect.collidepoint(mouse):
                    final_score, back = main.run_game(SCREEN)
                    save_high_score(final_score)

                    # reset menu state after returning from game
                    exit_anim = False
                    fireball.active = False
                    click.play()


                elif buttons[1].rect.collidepoint(mouse):
                    click.play()
                    story.run_story() 

                    pygame.display.set_mode((WIDTH, HEIGHT))
                    pygame.display.set_caption("Mukha Tejah : Mask Power System")

                elif buttons[2].rect.collidepoint(mouse):
                    show_modal("HIGH SCORE", f"{highscore}", duration=2000)

        if exit_anim and not fireball.active:
            pygame.quit()
            sys.exit()

        pygame.display.update()

# ------------------ RUN ------------------
if __name__ == "__main__":
    main_menu()
