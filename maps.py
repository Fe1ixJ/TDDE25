import images
import pygame
import json


class Map:
    """
    An instance of Map is a blueprint for how the game map will look.
    """

    def __init__(self, width, height, boxes, start_positions, flag_position):
        """
        Takes as argument the size of the map (width, height), an array with the boxes type,
        the start position of tanks (start_positions) and the position of the flag (flag_position).
        """
        self.width = width
        self.height = height
        self.boxes = boxes
        self.start_positions = start_positions
        self.flag_position = flag_position

    def rect(self):
        """
        Creates a rectangle with given size
        """
        return pygame.Rect(0, 0, images.TILE_SIZE * self.width, images.TILE_SIZE * self.height)

    def boxAt(self, x, y):
        """
        Return the type of the box at coordinates (x, y).
        """
        return self.boxes[y][x]


with open('maps/map0.json', 'r', encoding='utf-8') as file:
    map0_data = json.load(file)

map0 = Map(map0_data["width"], map0_data["height"], map0_data["boxes"], map0_data["tanks"], map0_data["flag"])

with open('maps/map1.json', 'r', encoding='utf-8') as file:
    map1_data = json.load(file)

map1 = Map(map1_data["width"], map1_data["height"], map1_data["boxes"], map1_data["tanks"], map1_data["flag"])


with open('maps/map2.json', 'r', encoding='utf-8') as file:
    map2_data = json.load(file)

map2 = Map(map2_data["width"], map2_data["height"], map2_data["boxes"], map2_data["tanks"], map2_data["flag"])


with open('maps/custom_map.json', 'r', encoding='utf-8') as file:
    custom_map_data = json.load(file)

custom_map = Map(custom_map_data["width"], custom_map_data["height"], custom_map_data["boxes"], custom_map_data["tanks"], custom_map_data["flag"])
