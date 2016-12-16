import libtcodpy as libtcod

class Object(object):
# This object class represents every visible object on the screen,
# shown with a character
	def __init__(self, x, y, char, name, color, blocks = False):
		self.name = name
		self.blocks = blocks
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		
	def move(self, map, objects, dx, dy):
		# Moves the object by the given amount
		try:
			if not self.is_blocked(map, objects, self.x + dx, self.y + dy):
				self.x += dx
				self.y += dy
		except IndexError:
			print("Trying to go out of map bounds at (" + str(self.x) + ", " + str(self.y) + ")")
		
	def draw(self, con, map, FOV):
		# Draws the object's character from the screen
		if(FOV):
			if libtcod.map_is_in_fov(map.fov_map, self.x, self.y):
				libtcod.console_set_default_foreground(con, self.color)
				libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
		else:
			libtcod.console_set_default_foreground(con, self.color)
			libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
	def clear(self, con):
		# Erases the object's character from the screen
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
		
	def update(self, map, objects):
		self.map = map
		pass
	
	def set_position(self, newPosition):
		self.x = newPosition[0]
		self.y = newPosition[1]
	
	def get_position(self):
		return (self.x, self.y)
		
	def is_blocked(self, map, objects, x, y):
		# First test the map tile
		if map.map[x][y].blocked:
			return True
		
		# Now we check for any blocking objects
		for obj in objects:
			if obj.blocks and obj.get_position() == (x, y) and obj != self:
				return True
		
		return False