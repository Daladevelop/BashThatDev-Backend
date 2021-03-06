#!/usr/bin/env python
import random
import sys
from player import Player
import random
MAP_SIZE = (40,9900)
class World:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.tiles = [[0 for i in range(self.height)] for i in range(self.width)]

		self.camera_width = 40
		self.camera_height = 20
		self.camera_offset = 0.0
		self.offset = [0,0]
		#check to see if camera normally would show anything above or under the map
		self.use_offset = False

	def get_visible_tiles(self, cam_y):
		
		
		visible_tiles = []

		for x in range(0, self.camera_width):
			row = []
			for y in range(0, self.camera_height):
				if cam_y +y >= self.height:
					row.append(self.tiles[0][0])
					
				else:
					row.append(self.tiles[x][cam_y + y])
			visible_tiles.append(row)

		return visible_tiles
	def __getitem__(self, index):
		return self.tiles[index]

	def get_offset(self):
		return self.offset

	def is_passable(self, x, y):
		x, y = int(x), int(y)
		#print "World.is_passable(%s, %s)" % (x, y)
		if x < 0 or x >= self.width:
			return False
		if y < 0 or y >= self.height:
			return False
		return (self[x][y] == 0)




def _create_test_world():
	"""FIXME: Temporary function for creating test world"""
	world = World(MAP_SIZE[0], MAP_SIZE[1])

	# Write walls
	for x in range(world.width):
		world[x][0] = 1
		world[x][world.height - 1] = 1
	for y in range(world.height):
		world[0][y] = 1
		world[world.width - 1][y] = 1

		x = random.randint(1,world.width-5)
		for i in range(random.randint(3,5)):
			world[x+i][y] = 1
		
	# Write platforms on bottom
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
