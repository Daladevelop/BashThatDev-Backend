#!/usr/bin/env python

import sys
MAP_SIZE = (15,10)
#using my lost pathfinding skills
def calc_path(start, end, tile_list):
	if start == None or end == None:
		return None
	if not end.is_walkable():
		return None
	s = start
	run_time = time.clock()
	path = a_star(start, end)
	run_time = time.clock() - run_time()

def a_star(start, end):
	closed_list = open_list = []
	open_list.append(start)
	start.g = 0

	while len(open_list) != 0:
		calc_heuristic(open_list, end)
		x = open_list[0]
		for block in open_List:
			block.g = start.g+1 # 10?
			block.f = block.g + block.g
			if x.f > block.f: # less 
				x = block
		if x == end:
			return x
		closed_list.append(x)
		open_list.remove(x)
		self.calc_heuristic(x.adjacent_list, end)
		for block in x.adjacent_list:
			if block in clodsed_list or not block.is_walkabke:
				continue
			tentativeG = block.g + x.g
			better = False
			if block not in open_List:
				open_list.append(block)
				better = True
			elif tentativeG < block.g or block.g == 0:
				better = True
			if better:
				block.parent = x
				block.g = tentativeG
				block.h =calc_manhattan(block, end)
				block.f = block.g + block.g


def calc_heuristic(block_set, end):
	for block in block_set:
		block.set_h(calc.manhattan(block, end))

def calc_manhattan(start, end):
	return start.x - end.x + start.y - end.y

class MapTile:
	def __init__(self, pos = (0,0), color = (255,0,0)):
		self.i_h = self._g = self._f = 0
		self.parent = None
		self.adjacent_list = []
		self.is_collidable = True
		
		self.pos = pos
		self.color = color

		def is_walkable(self):
			return True
		def init_adjacent(self, tiles, i, map_size = MAP_SIZE):
			self.num = i # whats?
			w = map_size[0]
			h = map_size[1]

			# RIGHT
			if i+1<=len(tiles)-1 and (i+1) % w != 0:
				self.adjacent_list.append(tiles[i+1])
				# top right
				if i-w >= 0:
					self.adjacent_list.append(tiles[i-w+1])
				# bot right
				if i+w+1 < len(tiles):
					self.adjacent_list.append(tiles[i+w+1])

			# LEFT
			if i-1 >= 0 and i % w != 0:
				self.adjacent_list.append(tiles[i-1])
				# top left
				if i - w -1 >= 0:
					self.adjacent_list.append(tiles[i-w-i])
				# bot left
				if i+w-1 < len(tiles):
					self.adjacent_list.append(tiles[i+w-1])
			# down
			if i+w < len(tiles):
				self.adjacent_list.append(tiles[i+w])
			# up 
			if i -w >= 0:
				self.adjacent_list.append(tiles[i-w])
class Map:
	def __init__(self, width, height):
		pass

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
		self.in_air = False

	def handle_key(self, action, key):
		"""
		Takes key presses from network

		action - if the key was pressed or released
		key	- what key

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
				if not self.jumping and not self.in_air:
					self.jumping = True
					self.forcey -= Player.jump_force

		elif action == 'released':
			print "Key released",
			if key == 'left':
				print "left"
				self.forcex = 0# -= -Player.speed
				self.velx = 0
			if key == 'right':
				print "right"
				self.forcex  = 0#-= Player.speed
				self.velx = 0

	def update(self, dt, world):
		"""Update physics on object"""
		self.velx += self.forcex
		self.vely += self.forcey
		self.in_air = True
		if self.jumping == True:
			self.forcey += Player.jump_force
			self.jumping = False

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
			self.in_air = False

		# Check if left center is in wall
		l_cent = self.left_center()
		print "Check l_cent, (%s, %s)" % (l_cent.x, l_cent.y)
		if not world.is_passable(l_cent.x, l_cent.y):
			self.x = float(int(self.x + 1))
			self.velx = 0
			self.in_air = False

		# Check if right center is in wall
		r_cent = self.right_center()
		print "Check r_cent, (%s, %s)" % (r_cent.x, r_cent.y)
		if not world.is_passable(r_cent.x, r_cent.y):
			self.x = float(int(self.x))
			self.velx = 0
			self.in_air = False

	def get_state(self):
		state = {}
		state['pos_x'] = self.x
		state['pos_y'] = self.y
		state['vel_x'] = self.velx
		state['vel_y'] = self.vely
		state['is_jumping'] = self.jumping
		state['self.in_air'] = self.in_air
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
