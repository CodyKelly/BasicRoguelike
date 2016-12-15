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
		self.explored = False
		
		# by default, if a tile is blocked, it also blocked sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight

class Map:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		
		self.color_dark_wall = libtcod.Color(0, 0, 100)
		self.color_light_wall = libtcod.Color(130, 110, 50)
		self.color_dark_ground = libtcod.Color(50, 50, 150)
		self.color_light_ground = libtcod.Color(200, 180, 50)
		
		self.fov_recompute = True
		
		self.make_map()
		self.make_fov_map()
				
	def update(self):
		if True in (libtcod.console_is_key_pressed(libtcod.KEY_UP),
		libtcod.console_is_key_pressed(libtcod.KEY_DOWN),
		libtcod.console_is_key_pressed(libtcod.KEY_LEFT),
		libtcod.console_is_key_pressed(libtcod.KEY_RIGHT)):
			self.fov_recompute = True
				
	def draw(self, con):
		for y in range(self.height):
			for x in range(self.width):
				visible = libtcod.map_is_in_fov(self.fov_map, x, y)
				wall = self.map[x][y].block_sight
				if not visible:
					# If the tile isn't visible by the player, first check to see 
					# if it has already been explored
					if self.map[x][y].explored:
						# If the tile has been explored, color it dark
						if wall:
							libtcod.console_set_char_background(con, x, y, self.color_dark_wall, libtcod.BKGND_SET)
						else:
							libtcod.console_set_char_background(con, x, y, self.color_dark_ground, libtcod.BKGND_SET)					
				else:
					# Color it light to show that it's within the player's FOV
					if wall:
						libtcod.console_set_char_background(con, x, y, self.color_light_wall, libtcod.BKGND_SET)
					else:
						libtcod.console_set_char_background(con, x, y, self.color_light_ground, libtcod.BKGND_SET)					
					self.map[x][y].explored = True
		
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
		
	def make_fov_map(self):
		self.fov_map = libtcod.map_new(self.width, self.height)
		
		for y in range(self.height):
			for x in range(self.width):
				libtcod.map_set_properties(self.fov_map, x, y, not self.map[x][y].block_sight, not self.map[x][y].blocked)
	
	def create_h_tunnel(self, x1, x2, y):
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.map[x][y].blocked = False
			self.map[x][y].block_sight = False
			
	def create_v_tunnel(self, y1, y2, x):
		for y in range(min(y1, y2), max(y1, y2) + 1):
			self.map[x][y].blocked = False
			self.map[x][y].block_sight = False
			
	def recompute_fov_map(self, player):
		libtcod.map_compute_fov(self.fov_map, player.x, player.y, player.view_radius, player.FOV_light_walls, player.FOV_algo)
		