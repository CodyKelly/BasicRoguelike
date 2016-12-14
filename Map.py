import libtcodpy as libtcod

class Rect:
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h

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