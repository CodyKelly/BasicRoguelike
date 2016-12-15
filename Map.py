import libtcodpy as libtcod

class Rect:
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h
	
	def center(self):
		center_x = (self.x1 + self.x2) / 2
		center_y = (self.y1 + self.y2) / 2
		return (center_x, center_y)
		
	def intersect(self, other):
		# Returns true if other rect overlaps this one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)

class Tile:
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked
		self.explored = False
		
		# by default, if a tile is blocked, it also blocked sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight

class Map:
	def __init__(self, width, height):
		# Width and height of map, in tiles
		self.width = width
		self.height = height
		
		# Tile colors
		self.color_dark_wall = libtcod.Color(0, 0, 100)
		self.color_light_wall = libtcod.Color(130, 110, 50)
		self.color_dark_ground = libtcod.Color(50, 50, 150)
		self.color_light_ground = libtcod.Color(200, 180, 50)
		
		# Dungeon generator variables
		self.room_max_size = 10
		self.room_min_size = 6
		self.max_rooms = 10
		self.center_of_first_room = (0, 0) # This will be changed when dungeon is generated
		
		# Tells the game if the fov map needs to be recomputed
		self.fov_recompute = True
		
		# Generate map
		self.make_map()
		self.make_fov_map()
				
	def update(self):
		if True in (libtcod.console_is_key_pressed(libtcod.KEY_UP),
		libtcod.console_is_key_pressed(libtcod.KEY_DOWN),
		libtcod.console_is_key_pressed(libtcod.KEY_LEFT),
		libtcod.console_is_key_pressed(libtcod.KEY_RIGHT)):
			self.fov_recompute = True
				
	def draw(self, con, FOV):
		for y in range(self.height):
			for x in range(self.width):
				if(FOV):
					visible = libtcod.map_is_in_fov(self.fov_map, x, y)
				else:
					visible = True
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
		# This fills the map with solid blocks to carve our rooms out of
		self.map = [[ Tile(True)
			for y in range(self.height) ]
				for x in range(self.width) ]
				
		rooms = []
		num_rooms = 0
		
		# This will loop through however many rooms we need to create
		# and assign random coordinates and size for each one
		for r in range(self.max_rooms):
			# Get a random width and height for the room
			w = libtcod.random_get_int(0, self.room_min_size, self.room_max_size)
			h = libtcod.random_get_int(0, self.room_min_size, self.room_max_size)
			
			# Get a random position within the boundaries of the map
			x = libtcod.random_get_int(0, 0, self.width - w - 1)
			y = libtcod.random_get_int(0, 0, self.height - h - 1)
		
			new_room = Rect(x, y, w, h)
			
			# Check to see if any of the other rooms overlap with this one
			failed = False
			for other_room in rooms:
				if new_room.intersect(other_room):
					failed = True
					break
			
			if not failed:
				# If there are no other overlapping rooms, create this one
				self.create_room(new_room)
				
				# Save the center coordinates of the new room to make tunnels later
				(newX, newY) = new_room.center()
				
				# Save the center of the first room to put the player in after
				if num_rooms == 0:
					self.center_of_first_room = new_room.center()
					
				else:
					# All rooms after the first connect to the previous one
					# with tunnels
					
					# First we get the center coordinates of the previous room
					(prevX, prevY) = rooms[num_rooms - 1].center()
					
					# Then we randomly choose whether to start with a vertical
					# or horizontal tunnel
					if libtcod.random_get_int(0, 0, 1) == 1:
						#first move horizontally, then vertically
						self.create_h_tunnel(prevX, newX, prevY)
						self.create_v_tunnel(prevY, newY, newX)
					else:
						#first move vertically, then horizontally
						self.create_v_tunnel(prevY, newY, prevX)
						self.create_h_tunnel(prevX, newX, newY)
				
				rooms.append(new_room)
				num_rooms += 1
		self.make_fov_map()
		
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
		
	def clear(self, con):
		self.map = []
		for y in range(self.height):
			for x in range(self.width):
				libtcod.console_set_char_background(con, x, y, libtcod.black, libtcod.BKGND_SET)