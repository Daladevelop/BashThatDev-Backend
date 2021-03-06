from rect import Rect
from point import Point

import logging

logger = logging.getLogger(__name__)

class Player(Rect):
	speed = 1.2
	jump_force = 20.0
	width = 1.
	height = 1.
	gravity = 1.23/100
	direction = 1 #right

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
		self.sfx_playlist = []

	def handle_key(self, action, key):
		"""
		Takes key presses from network

		action - if the key was pressed or released
		key - what key

		"""

		if action == 'pressed':
			#print "Key pressed",
			if key == 'left':
				#print "left"
				self.forcex += -Player.speed
				self.direction = 0
			if key == 'right':
				#print "right"
				self.forcex += Player.speed
				self.direction = 1
			if key == 'jump':
				#print "jump"
				if not self.jumping and not self.in_air:
					self.jumping = True
					self.forcey -= Player.jump_force

		elif action == 'released':
			#print "Key released",
			if key == 'left':
				#print "left"
				self.forcex = 0# -= -Player.speed
				self.velx = 0
			if key == 'right':
				#print "right"
				self.forcex  = 0#-= Player.speed
				self.velx = 0

	def update(self, dt, world):
		"""Update physics on object"""
		self.velx += self.forcex*dt
		self.vely += self.forcey*dt
		self.in_air = True
		if self.jumping == True:
			self.sfx_playlist.append('jump')
			self.forcey += Player.jump_force
			self.jumping = False

		self.vely += Player.gravity#*dt
		self.x += self.velx
		self.y += self.vely

		x, y = self.x, self.y
		width, height = self.width, self.height

		# Check if top center is in wall
		top_cent = self.top_center()
		if not world.is_passable(top_cent.x, top_cent.y):
			self.sfx_playlist.append('moose_scream')
			# Snap to bottom of world tile
			self.y = float(int(self.y + 1))
			self.vely = 0

		# Check if bottom center is in wall
		bot_cent = self.bottom_center()
		if not world.is_passable(bot_cent.x, bot_cent.y):
			self.y = float(int(self.y))
			self.vely = 0
			self.velx *= 0.95
			self.in_air = False

		# Check if left center is in wall
		l_cent = self.left_center()
		if not world.is_passable(l_cent.x, l_cent.y):
			self.x = float(int(self.x + 1))
			self.velx = 0
			#self.in_air = False

		# Check if right center is in wall
		r_cent = self.right_center()
		if not world.is_passable(r_cent.x, r_cent.y):
			self.x = float(int(self.x))
			self.velx = 0
			#self.in_air = False

	def get_state(self, cam_y):
		state = {}
		state['pos_x'] = self.x
		state['pos_y'] = self.y - cam_y
		state['vel_x'] = self.velx
		state['vel_y'] = self.vely
		state['is_jumping'] = self.jumping
		state['in_air'] = self.in_air
		state['sfx_playlist'] = self.sfx_playlist
		state['direction'] = self.direction
			
		self.sfx_playlist = []
		return state	
