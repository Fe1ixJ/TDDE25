"""
This file contains function and classes for the Artificial Intelligence used in the game.
"""

import math
from collections import defaultdict, deque

import pymunk
from pymunk import Vec2d
import gameobjects

# NOTE: use only 'map0' during development!

MIN_ANGLE_DIF = math.radians(3)  # 3 degrees, a bit more than we can turn each tick


def angle_between_vectors(vec1, vec2):
    """
    Since Vec2d operates in a cartesian coordinate space we have to
    convert the resulting vector to get the correct angle for our space.
    """
    vec = vec1 - vec2
    vec = vec.perpendicular()
    return vec.angle


def periodic_difference_of_angles(angle1, angle2):
    """
    Compute the difference between two angles.
    """
    return (angle1 % (2 * math.pi)) - (angle2 % (2 * math.pi))


class Ai:
    """
    A simple ai that finds the shortest path to the target using
    a breadth first search. Also capable of shooting other tanks and or wooden
    boxes.
    """

    def __init__(self, tank, game_objects_list, tanks_list, bullets_list, space, currentmap, FRAMERATE, coop, ai_contoll):
        self.tank = tank
        self.game_objects_list = game_objects_list
        self.tanks_list = tanks_list
        self.bullets_list = bullets_list
        self.space = space
        self.currentmap = currentmap
        self.flag = None
        self.max_x = currentmap.width - 1
        self.max_y = currentmap.height - 1
        self.FRAMERATE = FRAMERATE
        self.path = deque()
        self.move_cycle = self.move_cycle_gen()
        self.update_grid_pos()
        self.last_dif = None
        self.move_atemps = 0
        self.allow_metal = False
        self.target_tile = None
        self.ai_contoll = ai_contoll
        if self.ai_contoll:
            self.tank.make_ai(self, True)
        else:
            self.tank.make_ai(self, False)

    def update_grid_pos(self):
        """
        This should only be called in the beginning, or at the end of a move_cycle.
        """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)

    def decide(self):
        """
        Main decision function that gets called on every tick of the game.
        """
        next(self.move_cycle)
        self.maybe_shoot()

    def maybe_shoot(self):
        """
        Makes a raycast query in front of the tank. If another tank
        or a wooden box is found, then we shoot.
        """
        if self.ai_contoll:
            start = (
                self.tank.body.position + (0.3 * math.cos(self.tank.body.angle + math.pi / 2),
                                           (0.3 * math.sin(self.tank.body.angle + math.pi / 2)))
            )
            end = (
                self.tank.body.position + (100 * math.cos(self.tank.body.angle + math.pi / 2),
                                           (100 * math.sin(self.tank.body.angle + math.pi / 2)))
            )
            target = (self.space.segment_query_first(start, end, 0, pymunk.ShapeFilter()))
            shape = (hasattr(target, "shape"))
            parent = shape and (hasattr(target.shape, "parent"))
            destructable = parent and (hasattr(target.shape.parent, "destructable") and target.shape.parent.destructable)
            Tank = parent and (hasattr(target.shape.parent, "is_tank"))
            not_coop = (self.tank.team is None)
            coop = (Tank and hasattr(target.shape.parent, "team") and (target.shape.parent.team != self.tank.team))
            if destructable or (Tank and (not_coop or coop)):
                self.tank.shoot(self.bullets_list, self.space, self.FRAMERATE)

    def move_cycle_gen(self):
        """
        A generator that iteratively goes through all the required steps
        to move to our goal.
        """
        if not self.ai_contoll:
            while True:
                path = self.find_shortest_path()
                if not path:
                    yield
                    continue  # Start from the top of our cycle
                yield
                self.path = path
                self.update_grid_pos()
        while True:
            path = self.find_shortest_path()
            if not path:
                yield
                continue  # Start from the top of our cycle
            self.path = path
            next_coord = path.popleft()
            yield
            self.allow_metal = False
            self.turn(next_coord)
            while not self.corect_facing(next_coord):
                yield
            self.move_atemps = 0
            self.tank.stop_turning()
            self.tank.accelerate()
            while not self.corect_pos(next_coord):
                yield
            self.tank.stop_moving()
            self.update_grid_pos()

    def turn(self, next_coord):
        """
        Compares angle between tank and next_coord and starts turning if tank is not facing the correct way
        """
        temp_angle = angle_between_vectors(self.tank.body.position, next_coord + (0.5, 0.5))
        angle = periodic_difference_of_angles(self.tank.body.angle, temp_angle)
        if angle > math.pi:
            angle = - (2 * math.pi - angle)
        if angle < - math.pi:
            angle = (2 * math.pi - angle)
        if angle > 0:
            self.tank.turn_left()
        if angle < 0:
            self.tank.turn_right()

    def corect_facing(self, next_coord):
        """
        Checks if tank is facing the right way
        """
        temp_angle = angle_between_vectors(self.tank.body.position, next_coord + (0.5, 0.5))
        if -MIN_ANGLE_DIF < periodic_difference_of_angles(self.tank.body.angle, temp_angle) < MIN_ANGLE_DIF:
            return True
        return False

    def corect_pos(self, next_coord):
        """
        Checks if tank is where it wants. If it gets stuck or is pushed ii breaks the loop and resets
        """
        self.move_atemps += 1
        curent_dif = self.tank.body.position.get_distance(next_coord + (0.5, 0.5))
        if self.last_dif is not None:
            if curent_dif - 0.01 < self.last_dif < curent_dif + 0.01 and self.move_atemps > 10:
                self.last_dif = curent_dif
                return True
            if self.last_dif >= curent_dif:
                self.last_dif = curent_dif
                return False
            self.last_dif = curent_dif
            return True
        self.last_dif = curent_dif
        return False

    def find_shortest_path(self):
        """
        A simple Breadth First Search using integer coordinates as our nodes.
        Edges are calculated as we go, using an external function.
        """
        queue = deque()
        queue.append(self.grid_pos)
        visited = set()
        came_from = {}
        shortest_path = []
        visited.add(self.grid_pos.int_tuple)
        while queue:
            node = queue.popleft()
            if node == self.get_target_tile():
                while node in came_from:
                    shortest_path.append(node)
                    node = came_from[node]
                shortest_path.reverse()
                return deque(shortest_path)
            for neighbor in self.get_tile_neighbors(node):
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor.int_tuple)
                    came_from[neighbor] = node
        self.allow_metal = True

    def get_target_tile(self):
        """
        Returns position of the flag if we don't have it. If we do have the flag,
        return the position of our home base.
        """
        target = None
        for tank in self.tanks_list:
            if tank.flag and tank != self.tank:
                target = self.intercept(tank)
        if not target:
            if self.tank.flag is not None:
                x, y = self.tank.start_position
            else:
                self.get_flag()  # Ensure that we have initialized it.
                x, y = self.flag.x, self.flag.y
            target = Vec2d(int(x), int(y))
        self.target_tile = target
        return target

    def intercept(self, tank):
        target = tank.ai.target_tile
        for tile in tank.ai.path:
            if tile == self.grid_pos:
                target = tank.ai.grid_pos
        return target

    def get_flag(self):
        """
        This has to be called to get the flag, since we don't know
        where it is when the Ai object is initialized.
        """
        if self.flag is None:
            # Find the flag in the game objects list
            for obj in self.game_objects_list:
                if isinstance(obj, gameobjects.Flag):
                    self.flag = obj
                    break
        return self.flag

    def get_tile_of_position(self, position_vector):
        """
        Converts and returns the float position of our tank to an integer position.
        """
        x, y = position_vector
        return Vec2d(int(x), int(y))

    def get_tile_neighbors(self, coord_vec):
        """
        Returns all bordering grid squares of the input coordinate.
        A bordering square is only considered accessible if it is grass
        or a wooden box.
        """
        neighbors = []  # Find the coordinates of the tiles' four neighbors
        neighbors.append(coord_vec + (0, -1))  # upp
        neighbors.append(coord_vec + (0, 1))  # down
        neighbors.append(coord_vec + (-1, 0))  # left
        neighbors.append(coord_vec + (1, 0))  # right
        return filter(self.filter_tile_neighbors, neighbors)

    def filter_tile_neighbors(self, coord):
        """
        Used to filter the tile to check if it is a neighbor of the tank.
        """
        if (0 <= coord.x <= self.max_x) and (0 <= coord.y <= self.max_y):
            is_alowed = False
            is_alowed = is_alowed or self.currentmap.boxAt(coord.x, coord.y) == 0
            is_alowed = is_alowed or self.currentmap.boxAt(coord.x, coord.y) == 2
            is_alowed = is_alowed or (self.currentmap.boxAt(coord.x, coord.y) == 3 and self.allow_metal)
            return is_alowed
        return False
