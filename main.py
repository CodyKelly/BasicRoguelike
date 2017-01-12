import libtcodpy as libtcod
import Components
import math

################################################################################
#                               GLOBAL VARIABLES                               #
#           Variables here will be accessible throughout the program           #
################################################################################

# Window dimensions
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

# Map dimensions
MAP_WIDTH = 80
MAP_HEIGHT = 50

FOV = True # Is Field of View enabled?	
generateMonsters = True # Is the game generating monsters upon level creation?

# Set console font
libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_LAYOUT_TCOD)

# Initialize window
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)

# This list hold all objects in the game
objects = []

def player_death(player):
	global game_state
	print "You died!"
	game_state = "dead"
	
	player.char = '%'
	player.color = libtcod.dark_red

def monster_death(monster):
	print monster.name.capitalize() + " is dead!"
	monster.char = '%'
	monster.color = libtcod.dark_red
	monster.blocks = False
	monster.fighter = None
	monster.ai = None
	monster.name = "Remains of " + monster.name
	monster.send_to_back()

def render_all():
	if(FOV):
		if gameMap.fov_recompute:
			# If the map needs to recompute the FOV map, do it once
			gameMap.fov_recompute = False
			gameMap.recompute_fov_map(player)
			
	for obj in objects:
		if obj != player:
			obj.draw()
	player.draw()
	
	gameMap.draw()
		
	# Blit contents on the 'con' console to the root console
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	
	# Show the player's stats
	libtcod.console_set_default_background(con, libtcod.white)
	libtcod.console_print_ex(con, 1, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.LEFT,
		"HP: " + str(player.fighter.hp) + "/" + str(player.fighter.max_hp) + "      ")
	
def handle_keys():	
	global FOV, generateMonsters, player, gameMap, objects, game_state, player_action, con
	
	key = libtcod.console_wait_for_keypress(True)
	
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		# This makes alt + enter toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_F1:
		FOV = not FOV
		print("FOV: " + str(FOV))
	elif key.vk == libtcod.KEY_F2:
		generateMonsters = not generateMonsters
		print("Generate monsters = " + str(generateMonsters))
	elif key.c == ord('r'):
		con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
		
		objects = []
		
		gameMap = GameMap()
		gameMap.make_map()
		gameMap.make_fov_map()
		player = Player(gameMap.center_of_first_room[0], gameMap.center_of_first_room[1], '@', libtcod.white)
		objects.append(player)
		
		return "restart"
	elif key.vk == libtcod.KEY_ESCAPE:
		return "exit"	
	if game_state == "playing":
		return player.get_input()

class Rect(object):
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

class Tile(object):
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked
		self.explored = False
		
		# by default, if a tile is blocked, it also blocked sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight

class GameMap(object):
	def __init__(self):
		# Tile colors
		self.color_dark_wall = libtcod.Color(0, 0, 100)
		self.color_light_wall = libtcod.Color(130, 110, 50)
		self.color_dark_ground = libtcod.Color(50, 50, 150)
		self.color_light_ground = libtcod.Color(200, 180, 50)
		
		# Dungeon generator variables
		self.room_max_size = 10
		self.room_min_size = 6
		self.max_rooms = 30
		self.center_of_first_room = (0, 0) # This will be changed when dungeon is generated
		self.max_room_monsters = 6
		
		# Tells the game if the fov map needs to be recomputed
		self.fov_recompute = True
				
	def update(self):
		if True in (libtcod.console_is_key_pressed(libtcod.KEY_UP),
		libtcod.console_is_key_pressed(libtcod.KEY_DOWN),
		libtcod.console_is_key_pressed(libtcod.KEY_LEFT),
		libtcod.console_is_key_pressed(libtcod.KEY_RIGHT)):
			self.fov_recompute = True
				
	def draw(self):
		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):
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
			for y in range(MAP_HEIGHT) ]
				for x in range(MAP_WIDTH) ]
				
		rooms = []
		num_rooms = 0
		
		# This will loop through however many rooms we need to create
		# and assign random coordinates and size for each one
		for r in range(self.max_rooms):
			# Get a random width and height for the room
			w = libtcod.random_get_int(0, self.room_min_size, self.room_max_size)
			h = libtcod.random_get_int(0, self.room_min_size, self.room_max_size)
			
			# Get a random position within the boundaries of the map
			x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
			y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
		
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
				if(generateMonsters):
					self.place_objects(new_room, objects)
				rooms.append(new_room)
				num_rooms += 1
		self.make_fov_map()
		
	def make_fov_map(self):
		self.fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
		
		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):
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
		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):
				libtcod.console_set_char_background(con, x, y, libtcod.black, libtcod.BKGND_SET)
				
	def place_objects(self, room, objects):
		# Choose random number of monsters
		num_monsters = libtcod.random_get_int(0, 0, self.max_room_monsters)
		
		for i in range(num_monsters):
			# Choose a random spot for this monster
			x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
			y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
			
			if libtcod.random_get_int(0, 0, 100) < 80:	# 80% chance of getting an orc
				# Create and orc
				fighter_component = Components.Fighter(hp = 10, defense = 0, power = 3, death_function=monster_death)
				ai_component = Components.BasicMonster()
				
				monster = Object(x, y, 'o', "Orc", libtcod.desaturated_green, blocks=True, fighter = fighter_component, ai = ai_component)
			else:
				# Create a troll
				fighter_component = Components.Fighter(hp = 16, defense = 1, power = 4, death_function=monster_death)
				ai_component = Components.BasicMonster()
				
				monster = Object(x, y, 'T', "Troll", libtcod.darker_green, blocks=True, fighter = fighter_component, ai = ai_component)
				
			if not monster.is_blocked(x, y):
				objects.append(monster)
			else:
				print("Monster blocked at: (" + str(x) + ", " + str(y) + ")")
				
class Object(object):
# This object class represents every visible object on the screen,
# shown with a character
	def __init__(self, x, y, char, name, color, blocks = False, fighter = None, ai = None):
		self.name = name
		self.blocks = blocks
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.fighter = fighter
		if self.fighter:
			self.fighter.owner = self
		self.ai = ai
		if self.ai:
			self.ai.owner = self
		
	def move(self, dx, dy):
		# Moves the object by the given amount
		try:
			if not self.is_blocked(self.x + dx, self.y + dy):
				self.x += dx
				self.y += dy
		except IndexError:
			print("Trying to go out of map bounds at (" + str(self.x) + ", " + str(self.y) + ")")
		
	def draw(self):
		# Draws the object's character from the screen
		if(FOV):
			if libtcod.map_is_in_fov(gameMap.fov_map, self.x, self.y):
				libtcod.console_set_default_foreground(con, self.color)
				libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
		else:
			libtcod.console_set_default_foreground(con, self.color)
			libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
	def clear(self, con):
		# Erases the object's character from the screen
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
		
	def update(self):
		pass
	
	def set_position(self, newPosition):
		self.x = newPosition[0]
		self.y = newPosition[1]
	
	def get_position(self):
		return (self.x, self.y)
		
	def is_blocked(self, x, y):
		# First test the map tile
		if gameMap.map[x][y].blocked:
			return True
		
		# Now we check for any blocking objects
		for obj in objects:
			if obj.blocks and obj.get_position() == (x, y) and obj != self:
				return True
		
		return False
	
	def move_towards(self, target_x, target_y):
		dx = target_x - self.x
		dy = target_y - self.y
		
		distance = math.sqrt(dx ** 2 + dy ** 2)
		
		dx = int(round(dx / distance))
		dy = int(round(dy / distance))
		
		self.move(dx, dy)
	
	def distance_to(self, other):
		# Returns the distance to another object
		dx = other.x - self.x
		dy = other.y - self.y
		
		return math.sqrt(dx ** 2 + dy ** 2)
	
	def get_fov_map(self):
		return gameMap.fov_map
	
	def get_player(self):
		return player
	
	def send_to_back(self):
		# This method makes this object draw first, so other objects are drawn
		# on top of it.
		global objects
		objects.remove(self)
		objects.insert(0, self)

class Player(Object):
	def __init__(self, x, y, char, color, fighter):
		Object.__init__(self, x, y, char, "Player", color, blocks=True, fighter = fighter)
		
		self.FOV_algo = 0 # Default Field Of View algorithm
		self.FOV_light_walls = True
		
		self.view_radius = 10
	
	def update(self):
		super(Player, self).update()
	
	def move_or_attack(self, dx, dy):
		global fov_recompute
		
		# Calculate the coordinates the player is moving or attacking to
		x = self.x + dx
		y = self.y + dy
		
		# Detect any attackable object
		target = None
		for object in objects:
			if object.fighter and object.x == x and object.y == y:
				target = object
				break
		
		# If a target is found, attack, otherwise, move
		if target is not None:
			self.fighter.attack(target)
		else:
			player.move(dx, dy)
			fov_recompute = True
	
	def get_input(self):
		
		if(libtcod.console_is_key_pressed(libtcod.KEY_UP)):
			self.move_or_attack(0, -1)
	
		elif(libtcod.console_is_key_pressed(libtcod.KEY_DOWN)):
			self.move_or_attack(0, 1)
		
		elif(libtcod.console_is_key_pressed(libtcod.KEY_LEFT)):
			self.move_or_attack(-1, 0)
		
		elif(libtcod.console_is_key_pressed(libtcod.KEY_RIGHT)):
			self.move_or_attack(1, 0)
		else:
			return "didnt-take-turn"
	
################################################################################
#                                INITIALIZATION                                #
#        Things that need to be loaded at the start of the game go here        #
################################################################################
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

gameMap = GameMap()
gameMap.make_map()
gameMap.make_fov_map()

fighter_component = Components.Fighter(hp = 30, defense = 2, power = 5, death_function=player_death)
player = Player(gameMap.center_of_first_room[0], gameMap.center_of_first_room[1], '@', libtcod.white, fighter = fighter_component)

objects.append(player)
	
game_state = "playing"
player_action = None

################################################################################
#                                MAIN GAME LOOP                                #
#         Things here are repeated every time the player takes a turn          #
################################################################################

while not libtcod.console_is_window_closed():
	# Set the default console window to 'con', this is the main window
	libtcod.console_set_default_foreground(0, libtcod.white)
	
	for obj in objects:
		obj.update()
	
	gameMap.update()
	
	render_all()
	
	# Flush changes to the screen (this updates what is visible on-screen)
	libtcod.console_flush()
	
	for obj in objects:
		obj.clear(con)
	
	player_action = handle_keys()
	
	if player_action == "exit":
		break
		
	if game_state == "playing":
		for obj in objects:
			if obj.ai:
				obj.ai.take_turn()