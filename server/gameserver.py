import world
from world import Player, World
import world
PLAYER_BOT=world.MAP_SIZE[1]-5
import time
import logging
#test

campadding_y = 5
logger = logging.getLogger(__name__)

class GameEngine:
	def __init__(self):
		self.clients = {}
		self.keys = {32:'jump', 37:'left', 38:'up', 39:'right', 40:'down'}

		self.world = world._create_test_world()
		self.last_time = 0
		
	def handle(self, msg,peerstr):
		msg_type = msg['type']
		key = None
		try:
			key = self.keys[msg['keyCode']]
		except KeyError:
			pass

		self.clients[peerstr].handle_key(msg_type, key)

	def add_client(self, peerstr):
		if peerstr in self.clients.keys():
			print "du har kodat apa"
		else:
			self.clients[peerstr] = Player(peerstr, 2, PLAYER_BOT)

	def remove_client(self, peerstr):
		try:
			del self.clients[peerstr]
		except KeyError:
			print "oops client not in clients"


	def update(self):
		dt = time.time() - self.last_time
		self.last_time = time.time() # i do it here but i could do it... there
		for client in self.clients.values():
			client.update(dt,self.world)	

	def get_state(self):
		state = {}
		cam_y = self.world.height
		state['players'] = []

		min_y = self.world.height
		for client in self.clients.values():
			if client.y < min_y:
				min_y = client.y
				self.world.camera_offset = client.y - int(client.y)

		cam_y = min_y - campadding_y

		#loop through clients
		for client in self.clients.values():
			#append player
			state['players'].append( client.get_state( cam_y ) )
		print state['players']
		state['camera_offset'] = self.world.camera_offset
		state['world_width'] = self.world.camera_width
		state['world_height'] = self.world.camera_height
		state['world_tiles'] = self.world.get_visible_tiles(int(cam_y))

		return state
