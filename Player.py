from Object import Object
import libtcodpy as libtcod

class Player(Object):
	def __init__(self, x, y, char, color):
		Object.__init__(self, x, y, char, "Player", color, blocks=True)
		
		self.FOV_algo = 0 # Default Field Of View algorithm
		self.FOV_light_walls = True
		
		self.view_radius = 10
	
	def update(self, map, objects):
		super(Player, self).update(map, objects)
	
	def get_input(self, map, objects):
		if(libtcod.console_is_key_pressed(libtcod.KEY_UP)):
			self.move(map, objects, 0, -1)
	
		elif(libtcod.console_is_key_pressed(libtcod.KEY_DOWN)):
			self.move(map, objects, 0, 1)
		
		elif(libtcod.console_is_key_pressed(libtcod.KEY_LEFT)):
			self.move(map, objects, -1, 0)
		
		elif(libtcod.console_is_key_pressed(libtcod.KEY_RIGHT)):
			self.move(map, objects, 1, 0)
		
		return "didnt-take-turn"