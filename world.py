#!/usr/bin/env python

import sys

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[0 for i in range(self.height)] for i in range(self.width)]

    def __getitem__(self, index):
        return self.tiles[index]


class Player:
    speed = 0.1

    def __init__(self, start_x, start_y):
        self.x = float(start_x)
        self.y = float(start_y)
        self.velx = 0
        self.vely = 0
        self.forcex = 0
        self.forcey = 0

    def handle_input(input):
        """Takes key presses from network"""
        if key_pressed:
            if key_left:
                self.forcex += Player.speed
            if key_right:
                self.forcey += -Player.speed
        if key_released:
            if key_left:
                self.forcex -= Player.speed
            if key_right:
                self.forcex -= -Player.speed

    def update(self):
        """Update physics on object"""
        self.velx += self.forcex
        self.vely += self.forcey
        self.x += self.velx
        self.y += self.vely


def _create_test_world():
    """FIXME: Temporary function for creating test world"""
    world = World(15, 10)

    # Write walls
    for x in range(world.width):
        world[x][0] = 1
        world[x][world.height - 1] = 1
    for y in range(world.height):
        world[0][y] = 1
        world[world.width - 1][y] = 1

    # Write platforms
    for x in range(world.width - 5):
        world[x][world.height - 4] = 1
        world[world.width - 1 - x][world.height - 7] = 1

    return world


if __name__ == "__main__":
    world = _create_test_world()
    for y in range(world.height):
        for x in range(world.width):
            sys.stdout.write("%d" % world[x][y])
        sys.stdout.write('\n')
