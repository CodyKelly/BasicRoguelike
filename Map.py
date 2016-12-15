import libtcodpy as libtcod

class Rect:
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h
	
	def center(self):
		centerX = (self.x1 + self.x2) / 2
		centerY = (self.y1 + self.y2) / 2
		return (centerX, centerY)
		
	def intersection(self, other):
		# This returns true if this rectangle and the other intersects
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)

class Tile:
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked
		
		# by default, if a tile is blocked, it also blocked sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight

class Map:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		
		self.color_dark_wall = libtcod.Color(0, 0, 100)
		self.color_dark_ground = libtcod.Color(50, 50, 150)
		
		self.make_map()
				
	def draw(self, con):
		for y in range(self.height):
			for x in range(self.width):
				wall = self.map[x][y].block_sight
				if wall:
					libtcod.console_set_char_background(con, x, y, self.color_dark_wall, libtcod.BKGND_SET)
				else:
					libtcod.console_set_char_background(con, x, y, self.color_dark_ground, libtcod.BKGND_SET)					
		
	def create_room(self, rect):
		for x in range(rect.x1 + 1, rect.x2):
			for y in range(rect.y1 + 1, rect.y2):
				self.map[x][y].blocked = False
				self.map[x][y].block_sight = False
				
	def make_map(self):
		self.map = [[ Tile(True)
			for y in range(self.height) ]
				for x in range(self.width) ]
				
		room1 = Rect(20,15,10,15)
		room2 = Rect(50, 15, 10, 15)
		
		self.create_room(room1)
		self.create_room(room2)	
		
		self.create_h_tunnel(25, 55, 23)
	
	def create_h_tunnel(self, x1, x2, y):
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.map[x][y].blocked = False
			self.map[x][y].block_sight = False
			
	def create_v_tunnel(self, y1, y2, x):
		for y in range(min(y1, y2), max(y1, y2) + 1):
			self.map[x][y].blocked = False
			self.map[x][y].block_sight = False