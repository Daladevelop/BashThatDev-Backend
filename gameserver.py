import world
from world import Player, World
import world
PLAYER_BOT=world.MAP_SIZE[1]-5
import time
#test

campadding_y = 3

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
		cam_y = 0
		highest_player = self.world.height
		state['players'] = []
		for client in self.clients.values():
			#if current player is the highest
			if client.y	< highest_player:
				cam_y = client.y - campadding_y
				self.world.camera_offset = client.y - int(client.y)
			
			#append player
			state['players'].append( client.get_state( cam_y ) )
		

		state['world_width'] = self.world.camera_width
		state['world_height'] = self.world.camera_height
		state['world_tiles'] = self.world.get_visible_tiles(int(cam_y))

		return state
