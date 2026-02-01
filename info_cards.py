import pygame
import textwrap

class InfoCards:
    def __init__(self, screen):
        self.screen = screen
        self.active = False
        self.index = 0

        self.W, self.H = screen.get_size()

        self.font = pygame.font.Font(
            "assets/fonts/MinecraftRegular-Bmg3.otf", 18
        )

        self.italic_font = pygame.font.SysFont(
            "arial", 18, italic=True
        )

        self.title_font = pygame.font.Font(
            "assets/fonts/MinecraftRegular-Bmg3.otf", 28
        )

        self.name_font = pygame.font.SysFont(
            "arial", 26, bold=True
        )




        # -------------------------
        # LOAD CARD IMAGES
        # -------------------------
        self.cards = [
            {
                "name": "THEYYAM",
                "image": pygame.image.load("assets/cards/theyyam_card.png").convert_alpha(),
                "text": {
                    "lore": "Born from the sacred Theyyam rituals of Kerala, this mask channels ancestral spirits through fire and devotion.",
                    "abilities": [
                        "Ranged Fireball [SPACE]",
                    ],
                    "weaknesses": [
                        "Low speed",
                    ]
                    }

            },
            {
                "name": "KALI",
                "image": pygame.image.load("assets/cards/kali_card.png").convert_alpha(),
                "text": {
                    "lore": "Rooted in Hindu mythology, Kali represents destruction and rebirth, feared as the devourer of demons and ego alike.",
                    "abilities": [
                        "Sword Melee [SPACE]",
                        "Charging Melee [Q]",
                    ],
                    "weaknesses": [
                        "Limited vision in darkness",
                    ]
                }
            },

            {
                "name": "GARUDA",
                "image": pygame.image.load("assets/cards/garuda_card.png").convert_alpha(),
                "text": {
                    "lore": "Inspired by Garuda, the divine mount of Vishnu, this mask draws power from ancient Vedic legends of speed and vigilance.",
                    "abilities": [
                        "Extreme movement speed",
                    ],
                    "weaknesses": [
                        "Stunned upon hit by enemies",
                    ]
                }
            },

        ]

        # -------------------------
        # SCALE CARDS
        # -------------------------
        self.card_size = (520, 520)
        for c in self.cards:
            c["image"] = pygame.transform.scale(c["image"], self.card_size)

        # -------------------------
        # TEXT SETTINGS
        # -------------------------
        self.font = pygame.font.Font(
            "assets/fonts/MinecraftRegular-Bmg3.otf", 18
        )

        self.text_color = (59, 59, 59)

        # Text padding inside card image
        self.text_rect = pygame.Rect(
            40,   # left
            250,  # top
            440,  # width
            180   # height
        )

    # -------------------------
    # OPEN / CLOSE
    # -------------------------
    def open(self):
        self.active = True
        self.index = 0

    def close(self):
        self.active = False

    # -------------------------
    # INPUT
    # -------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_DOWN):
                self.close()

            elif event.key == pygame.K_RIGHT:
                self.index = (self.index + 1) % len(self.cards)

            elif event.key == pygame.K_LEFT:
                self.index = (self.index - 1) % len(self.cards)

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self):
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        

        card = self.cards[self.index]
        image = card["image"]

        # Center card
        rect = image.get_rect(center=(self.W // 2, self.H // 2))
        self.screen.blit(image, rect)


        # Draw wrapped text
        self.draw_card_text(
            card,
            rect.x + self.text_rect.x,
            rect.y + self.text_rect.y
        )


        # Page indicator
        page = f"{self.index + 1}/{len(self.cards)}"
        page_text = self.font.render(page, True, (50, 50, 50))
        self.screen.blit(
            page_text,
            (rect.centerx - page_text.get_width() // 2, rect.bottom + 10)
        )

    # -------------------------
    # TEXT WRAPPING
    # -------------------------
    def draw_card_text(self, card, x, y):
        line_gap = 6
        cursor_y = y

        # ---- CARD NAME (BOLD, CENTERED) ----
        name_surface = self.title_font.render(
            card["name"], True, (0, 0, 0)
        )

        name_x = x + (self.text_rect.width // 2) - (name_surface.get_width() // 2)

        self.screen.blit(name_surface, (name_x, cursor_y))
        cursor_y += name_surface.get_height() + 12



        # ---- LORE (ITALIC, WRAPPED) ----
        max_width = self.text_rect.width
        words = card["text"]["lore"].split(" ")
        line = ""
        wrapped_lines = []

        for word in words:
            test_line = line + word + " "
            test_surface = self.italic_font.render(test_line, True, (49, 49, 49))

            if test_surface.get_width() <= max_width:
                line = test_line
            else:
                wrapped_lines.append(line)
                line = word + " "

        if line:
            wrapped_lines.append(line)

        for l in wrapped_lines:
            lore_surface = self.italic_font.render(l, True, (20, 20, 20))
            self.screen.blit(lore_surface, (x, cursor_y))
            cursor_y += lore_surface.get_height() + 4

        cursor_y += 14


        # ---- ABILITIES ----
        title = self.font.render("Abilities", True, (155, 100, 40))
        self.screen.blit(title, (x, cursor_y))
        cursor_y += title.get_height() + 6

        for ability in card["text"]["abilities"]:
            line = self.font.render(f"• {ability}", True, (20, 20, 20))
            self.screen.blit(line, (x + 10, cursor_y))
            cursor_y += line.get_height() + line_gap

        cursor_y += 12

        # ---- WEAKNESSES ----
        title = self.font.render("Weaknesses", True, (155, 45, 45))
        self.screen.blit(title, (x, cursor_y))
        cursor_y += title.get_height() + 6

        for weak in card["text"]["weaknesses"]:
            line = self.font.render(f"• {weak}", True, (20, 20, 20))
            self.screen.blit(line, (x + 10, cursor_y))
            cursor_y += line.get_height() + line_gap

