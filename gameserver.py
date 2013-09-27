import world
from world import Player, World
import time
#test
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
			self.clients[peerstr] = Player(peerstr, 2, 2)

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
		state['world_width'] = self.world.width
		state['world_height'] = self.world.height
		state['world_tiles'] = self.world.tiles	
		state['players'] = []
		for client in self.clients.values():
			state['players'].append(client.get_state())

		return state
