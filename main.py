import libtcodpy as libtcod
import math
import textwrap

################################################################################
#                               GLOBAL VARIABLES                               #
#           Variables here will be accessible throughout the program           #
################################################################################

# FPS limit
LIMIT_FPS = 60

# Window dimensions
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

# Map dimensions
MAP_WIDTH = 80
MAP_HEIGHT = 43

MAX_ROOM_ITEMS = 2

# Sizes and position of the gui
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

INVENTORY_WIDTH = 50

FOV = True # Is Field of View enabled?	
generateMonsters = True # Is the game generating monsters upon level creation?

# Set console font
libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_LAYOUT_TCOD)

# Initialize window
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)

# This list holds all objects in the game
objects = []

# This list holds all the GUI messages for the player
game_msgs = []

# The player's inventory
inventory = []

def player_death(player):
	global game_state
	message("You died!", libtcod.light_red)
	game_state = "dead"
	
	player.char = '%'
	player.color = libtcod.dark_red

def monster_death(monster):
	message(monster.name.capitalize() + " is dead!", libtcod.light_blue)
	monster.char = '%'
	monster.color = libtcod.dark_red
	monster.blocks = False
	monster.remove_component("Fighter")
	monster.remove_component("BasicMonster")
	monster.name = "Remains of " + monster.name
	monster.send_to_back()

def message(new_msg, color = libtcod.white):
	# First we'll split the message if necessary into multiple lines (text wrapping)
	new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
	
	for line in new_msg_lines:
		# If the buffer is full, remove the first line to make room for the
		# new line.
		if len(game_msgs) == MSG_HEIGHT:
			del game_msgs[0]
		
		# Add the new line as a tuple, with the text and the color
		game_msgs.append((line, color))
	
def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
	# Renders a status bar (for HP, experience points, etc.)
	
	# First we'll calculate the width of the bar
	bar_width = int(float(value) / maximum * total_width)
	
	# Then we'll render the background
	libtcod.console_set_default_background(panel, back_color)
	libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
	
	# Now we render the bar on top of the background
	libtcod.console_set_default_background(panel, back_color)
	if bar_width > 0:
		libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
		
	# And now we'll put some text above the bar, displaying the actual values
	libtcod.console_set_default_foreground(panel, libtcod.white)
	libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, "{0}: {1}/{2}".format(name, value, maximum))

def menu(header, options, width):
	if len(options) > 26:
		raise ValueError("Cannot have a menu with more than 26 options")
	
	# Calculate total height for the header (after auto-wrap) and one line per options
	header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
	height = len(options) + header_height
	
	# Create an off-screen console that represents the menu's window
	window = libtcod.console_new(width, height)
	
	# Print the header, with auto-wrap
	libtcod.console_set_default_foreground(window, libtcod.white)
	libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
	
	# Print all the options
	y = header_height
	letter_index = ord("a")
	
	for option_text in options:
		text = "({0}) {1}".format(chr(letter_index), option_text)
		libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
		y += 1
		letter_index += 1

	# Blit the contents of "window" to the root console
	x = SCREEN_WIDTH / 2 - width / 2
	y = SCREEN_HEIGHT / 2 - height / 2
	
	# The last two parameters of this next function control the foreground transparency
	# and the background transparency, respectively
	libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
	
	# Present the root console to the player and wait for a key press
	libtcod.console_flush()
	key = libtcod.console_wait_for_keypress(True)
	
	# Convert the ASCII code to an index; if it corresponds to an option, return it
	index = key.c - ord('a')
	
	if index >= 0 and index < len(options): return index
	return None

def inventory_menu(header):
	# Show a menu with each item of the inventory as an option_text
	if len(inventory) == 0:
		options = ["Inventory is empty."]
	else:
		options = [item.name for item in inventory]
		
	index = menu(header, options, INVENTORY_WIDTH)
	if index is None or not len(inventory): return None
	return inventory[index].get_component("Item")	
	
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
	libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)
	
	# Prepare the gui panel for rendering
	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)
	
	# First we'll render the log messages
	y = 1
	for (line, color) in game_msgs:
		libtcod.console_set_default_foreground(panel, color)
		libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
		y += 1
	
	# Show the player's stats
	render_bar(1, 1, BAR_WIDTH, "HP", player.get_component("Fighter").hp, player.get_component("Fighter").max_hp, libtcod.light_red, libtcod.darker_red)
	
	# Display the names of objects under the mouse
	libtcod.console_set_default_foreground(panel, libtcod.light_grey)
	libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())
	
	# Blit the contents of "panel" to the root console
	libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)
	
def get_names_under_mouse():
	global mouse
	
	# Return a string with the names of all the objects under the mouse
	(x, y) = (mouse.cx, mouse.cy)
	
	# Create a list with the names of all objects at the mouse's coordinates and in the FOV
	names = [obj.name for obj in objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(gameMap.fov_map, obj.x, obj.y)]
	
	names = ', '.join(names) # Joins all the names together, seperated by commas
	
	return names.capitalize()
	
def handle_keys():	
	global FOV, generateMonsters, player, game_state, key
		
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		# This makes alt + enter toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_F1:
		FOV = not FOV
	elif key.vk == libtcod.KEY_F2:
		generateMonsters = not generateMonsters
	elif key.vk == libtcod.KEY_ESCAPE:
		return "exit"	
	
	if game_state == "playing":
		return player.get_input()
	
class Component:
	def __init__(self, name):
		self.name = name
	
	def update(self):
		pass

class Fighter(Component):
	# Combat-related properties and methods
	def __init__(self, hp, defense, power, death_function=None):
		Component.__init__(self, "Fighter")
		self.max_hp = hp
		self.hp = hp
		self.defense = defense
		self.power = power
		self.death_function = death_function
		
	def take_damage(self, damage):
		# Apply damage
		if damage > 0:
			self.hp -= damage
		
		if self.hp <= 0:
			self.hp = 0
			function = self.death_function
			if function is not None:
				function(self.owner)
			
	def attack(self, target):
		damage = self.power - target.get_component("Fighter").defense
		
		if damage > 0:
			# Make the target take damage
			color = libtcod.light_red
			if(self.owner == player):
				color = libtcod.light_blue
			message(self.owner.name.capitalize() + " attacks " + target.name + " for " + str(damage) + " hit points.", color)
				
			target.get_component("Fighter").take_damage(damage)
		else:
			print self.owner.name.capitalize() + " attacks " + target.name + " but it has no effect!"

class BasicMonster(Component):
	def __init__(self):
		Component.__init__(self, "BasicMonster")
	# AI for a monster
	def update(self):
		monster = self.owner
		player = monster.get_player()
		
		if libtcod.map_is_in_fov(monster.get_fov_map(), monster.x, monster.y):
		
			if monster.distance_to(player) >= 2:
				monster.move_towards(player.x, player.y)
			
			elif player.get_component("Fighter").hp > 0:
				monster.get_component("Fighter").attack(player)		

class Item(Component):
	def __init__(self, use_function=None):
		Component.__init__(self, "Item")
		self.use_function = use_function
	# This allows an object to be picked up and used
	def pick_up(self):
		# Add self to player's inventory and remove from the map
		if len(inventory) >= 26:
			message("Your inventory is full, cannot pick up {0}.".format(self.owner.name), libtcod.red)
		else:
			objects.remove(self.owner)
			inventory.append(self.owner)
			message("You picked up a {0}!".format(self.owner.name), libtcod.green)
	
	def use(self):
		# Calls the use_function
		if not self.use_function:
			message("The {0} cannot be used.".format(self.owner.name))
		else:
			if self.use_function() != 'cancelled':
				inventory.remove(self.owner) # Destroy after use, unless it was cancelled for some reason
				
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
		# Choose random number of monsters and items
		num_monsters = libtcod.random_get_int(0, 0, self.max_room_monsters)
		num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)
		
		# First we'll place the monsters
		for i in range(num_monsters):
			# Choose a random spot for this monster
			x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
			y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
			
			if libtcod.random_get_int(0, 0, 100) < 80:	# 80% chance of getting an orc
				# Create and orc
				fighter_component = Fighter(hp = 10, defense = 0, power = 3, death_function=monster_death)
				ai_component = BasicMonster()
				
				monster = Object(x, y, 'o', "Orc", libtcod.desaturated_green, blocks=True, components=[fighter_component, ai_component])
			else:
				# Create a troll
				fighter_component = Fighter(hp = 16, defense = 1, power = 4, death_function=monster_death)
				ai_component = BasicMonster()
				
				monster = Object(x, y, 'T', "Troll", libtcod.darker_green, blocks=True, components=[fighter_component, ai_component])
				
			if not monster.is_blocked(x, y):
				objects.append(monster)
				
		# And now the items
		for i in range(num_items):
			# We'll choose a random spot for this item
			x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
			y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
			
			# We'll only place it if the tile isn't blocked
			itemComp = Item()
			item = Object(x, y, "!", "Healing potion", libtcod.violet, False, [itemComp])
			
			if not item.is_blocked(x, y):
				objects.append(item)
				item.send_to_back()
		
class Object(object):
# This object class represents every visible object on the screen,
# shown with a character
	def __init__(self, x, y, char, name, color, blocks = False, components=[]):
		self.name = name
		self.blocks = blocks
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.components = components
		
		for c in self.components:
			c.owner = self
		
	def move(self, dx, dy):
		# Moves the object by the given amount
		if not self.is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy
		
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
		for c in self.components:
			c.update()
	
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
	
	def add_component(self, newComponent):
		already_has_component = False
		for component in self.components:
			if newComponent.name == component.name:
				already_has_component = True
				break
		if not already_has_component:
			self.components.append(newComponent)
			newComponent.owner = self
	
	def get_component(self, name):
		for c in self.components:
			if c.name == name:
				return c
		return None
		
	def remove_component(self, name):
		for c in self.components:
			if c.name == name:
				self.components.remove(c)

	@property
	def position(self):
		return (self.x, self.y)
	
	@position.setter
	def position(self, position):
		(self.x, self.y) = position
	
class Player(Object):
	def __init__(self, x, y, char, color, comps=[]):
		Object.__init__(self, x, y, char, "Player", color, blocks=True, components=comps)
		
		self.FOV_algo = 0 # Default Field Of View algorithm
		self.FOV_light_walls = True
		
		self.view_radius = 10
		
		self.action = None
	
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
			if object.get_component("Fighter") and object.x == x and object.y == y:
				target = object
				break
		
		# If a target is found, attack, otherwise, move
		if target is not None:
			self.get_component("Fighter").attack(target)
		else:
			player.move(dx, dy)
			gameMap.fov_recompute = True
			
		self.action = "moved"
	
	def get_input(self):
		global key
		self.action = None
		
		if(key.vk == libtcod.KEY_UP):
			self.move_or_attack(0, -1)
	
		elif(key.vk == libtcod.KEY_DOWN):
			self.move_or_attack(0, 1)
		
		elif(key.vk == libtcod.KEY_LEFT):
			self.move_or_attack(-1, 0)
		
		elif(key.vk == libtcod.KEY_RIGHT):
			self.move_or_attack(1, 0)
		
		if not self.action:
			# Test for other keys if we haven't moved
			key_char = chr(key.c)
			
			if key_char == 'g':
				# Pick up an item
				for object in objects: # Look for an item under player
					if object.position == self.position:
						itemComp = object.get_component("Item")
						if(itemComp):
							itemComp.pick_up()
							self.action = "picked_up_item"
							break
						
			elif key_char == "i":
				# Show inventory
				chosenItem = inventory_menu("Press the key next to an item to use it, or any other to cancel.\n")
				if chosenItem:
					chosenItem.use()
			
		return self.action
	
################################################################################
#                                INITIALIZATION                                #
#        Things that need to be loaded at the start of the game go here        #
################################################################################
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

gameMap = GameMap()
gameMap.make_map()
gameMap.make_fov_map()

fighter_component = Fighter(hp = 30, defense = 2, power = 5, death_function=player_death)
player = Player(gameMap.center_of_first_room[0], gameMap.center_of_first_room[1], '@', libtcod.white)
player.add_component(fighter_component)

objects.append(player)
	
game_state = "playing"

# Set the default console window to 'con', this is the main window
libtcod.console_set_default_foreground(0, libtcod.white)

mouse = libtcod.Mouse()
key = libtcod.Key()

# Render everything
render_all()

for obj in objects:
	obj.clear(con)
	
libtcod.console_flush()

libtcod.sys_set_fps(LIMIT_FPS)

message("Welcome to the scariest and most monster-filled dungeon of ALL-TIME!! YOU SHALL NOT SURVIVE!!!!!!!")

################################################################################
#                                MAIN GAME LOOP                                #
#         Things here are repeated every time the player takes a turn          #
################################################################################

while not libtcod.console_is_window_closed():
	libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

	player_action = handle_keys()
	
	if player_action == "exit":
		break
	
	player.update()
	
	for obj in objects:
		if obj != player and player.action == "moved":
			obj.update()
			
	render_all()
	
	for obj in objects:
		obj.clear(con)
		
	# Flush changes to the screen (this updates what is visible on-screen)
	libtcod.console_flush()