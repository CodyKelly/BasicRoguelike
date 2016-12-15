import libtcodpy as libtcod

class Object(object):
# This object class represents every visible object on the screen,
# shown with a character
	def __init__(self, x, y, char, color):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		
	def move(self, dx, dy):
		# Moves the object by the given amount
		try:
			if not self.map.map[self.x + dx][self.y + dy].blocked:
				self.x += dx
				self.y += dy
		except IndexError:
			print("Trying to go out of map bounds at (" + str(self.x) + ", " + str(self.y) + ")")
		
	def draw(self, con, map):
		# Draws the object's character from the screen
		if libtcod.map_is_in_fov(map.fov_map, self.x, self.y):
			libtcod.console_set_default_foreground(con, self.color)
			libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
		
	def clear(self, con):
		# Erases the object's character from the screen
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
		
	def update(self, map, objects):
		self.map = map
		pass