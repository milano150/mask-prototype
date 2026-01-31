import pygame
from pytmx.util_pygame import load_pygame


class MapLoader:
    def __init__(self, tmx_path):
        # Load TMX file
        self.tmx_data = load_pygame(tmx_path)

        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight

        self.map_width = self.tmx_data.width * self.tile_width
        self.map_height = self.tmx_data.height * self.tile_height

        # Surface where the map will be drawn
        self.map_surface = pygame.Surface(
            (self.map_width, self.map_height)
        ).convert_alpha()

        self.walls = []
        self.doors = []
        self.player_spawn = None

        self._draw_map()
        self._load_objects()

    # ----------------------------
    # Draw tile layers
    # ----------------------------
    def _draw_map(self):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, tile in layer.tiles():
                    if tile:
                        self.map_surface.blit(
                            tile,
                            (x * self.tile_width, y * self.tile_height)
                        )

    # ----------------------------
    # Read object layers
    # ----------------------------
    def _load_objects(self):
        for obj in self.tmx_data.objects:
            rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

            if obj.type == "wall":
                self.walls.append(rect)

            elif obj.type == "door":
                self.doors.append({
                    "rect": rect,
                    "locked": obj.properties.get("locked", True)
                })

            elif obj.type == "spawn":
                self.player_spawn = (obj.x, obj.y)

    # ----------------------------
    # Draw map to screen
    # ----------------------------
    def draw(self, screen, camera_offset=(0, 0)):
        screen.blit(
            self.map_surface,
            (-camera_offset[0], -camera_offset[1])
        )
