""" OLD STUFF, NEVER USED & OTHER """

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


