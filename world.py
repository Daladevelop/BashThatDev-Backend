#!/usr/bin/env python

import sys

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[0 for i in range(self.height)] for i in range(self.width)]

    def __getitem__(self, index):
        return self.tiles[index]

    def is_passable(self, x, y):
        x, y = int(x), int(y)
	print "World.is_passable(%s, %s)" % (x, y)
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False
        return self[x][y] == 0


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, x, y, w, h):
        self.x = float(x)
        self.y = float(y)
        self.w = float(w)
        self.h = float(h)

    def min_x(self):
        return self.x

    def min_y(self):
        return self.y

    def max_x(self):
        return self.x + self.w

    def max_y(self):
        return self.y + self.h

    def center(self):
        return Point((self.min_x() + self.max_x()) / 2, (self.min_y() + self.max_y()) / 2)

    def left_center(self):
        return Point(self.min_x(), (self.min_y() + self.max_y()) / 2)

    def right_center(self):
        return Point(self.max_x(), (self.min_y() + self.max_y()) / 2) 

    def top_center(self):
        return Point((self.min_x() + self.max_x()) / 2, self.min_y())

    def bottom_center(self):
        return Point((self.min_x() + self.max_x()) / 2, self.max_y())


class Player(Rect):
    speed = 0.1
    jump_force = 1.0
    width = 1.
    height = 1.
    gravity = 0.05

    def __init__(self, uid, start_x, start_y):
        Rect.__init__(self, start_x, start_y,
                Player.width, Player.height)
        self.uid = uid
        self.velx = 0
        self.vely = 0
        self.forcex = 0
        self.forcey = 0
        self.jumping = False

    def handle_key(self, action, key):
        """
        Takes key presses from network

        action - if the key was pressed or released
        key    - what key

        """

        print "Key received: action(%s), key(%s)" % (action, key)

        if action == 'pressed':
            print "Key pressed",
            if key == 'left':
                print "left"
                self.forcex += -Player.speed
            if key == 'right':
                print "right"
                self.forcex += Player.speed
            if key == 'jump':
                print "jump"
                if not self.jumping:
                    self.jumping = True
                    self.forcey -= Player.jump_force

        elif action == 'released':
            print "Key released",
            if key == 'left':
                print "left"
                self.forcex -= -Player.speed
            if key == 'right':
                print "right"
                self.forcex -= Player.speed

    def update(self, dt, world):
        """Update physics on object"""
        self.velx += self.forcex
        self.vely += self.forcey

        if self.jumping == True:
            self.jumping = False
            self.forcey += Player.jump_force

        self.vely += Player.gravity
        self.x += self.velx
        self.y += self.vely
        print "x=%.2f y=%.2f xv=%.2f yv=%.2f" % (self.x, self.y,
                self.velx, self.vely)

        x, y = self.x, self.y
        width, height = self.width, self.height

        # Check if top center is in wall
        top_cent = self.top_center()
	print "Check top_cent, (%s, %s)" % (top_cent.x, top_cent.y)
        if not world.is_passable(top_cent.x, top_cent.y):
            # Snap to bottom of world tile
            self.y = float(int(self.y + 1))
            self.vely = 0

        # Check if bottom center is in wall
        bot_cent = self.bottom_center()
	print "Check bot_cent, (%s, %s)" % (bot_cent.x, bot_cent.y)
        if not world.is_passable(bot_cent.x, bot_cent.y):
            self.y = float(int(self.y))
            self.vely = 0
            self.velx *= 0.8

        # Check if left center is in wall
        l_cent = self.left_center()
	print "Check l_cent, (%s, %s)" % (l_cent.x, l_cent.y)
        if not world.is_passable(l_cent.x, l_cent.y):
            self.x = float(int(self.x + 1))
            self.velx = 0

        # Check if right center is in wall
        r_cent = self.right_center()
	print "Check r_cent, (%s, %s)" % (r_cent.x, r_cent.y)
        if not world.is_passable(r_cent.x, r_cent.y):
            self.x = float(int(self.x))
            self.velx = 0

    def get_state(self):
        state = {}
        state['pos_x'] = self.x
        state['pos_y'] = self.y
        state['vel_x'] = self.velx
        state['vel_y'] = self.vely
        state['is_jumping'] = self.jumping
        return state


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

    player = Player(2, 2)

    while(True):
        player.update(world)
