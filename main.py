import libtcodpy as libtcod
from Object import Object
from Player import Player
from Map import Map

# Window dimensions
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

# Set console font
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_LAYOUT_TCOD)

# Initialize window
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
	
FOV = True # This controls whether FOV is enabled or not	
generateMonsters = True
	
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
map = Map(80, 50)
player = Player(0, 0, '@', libtcod.white)
objects = [player]

def render_all():
	for obj in objects:
		obj.draw(con, map, FOV)
		
	if(FOV):
		if map.fov_recompute:
			# If the map needs to recompute the FOV map, do it once
			map.fov_recompute = False
			map.recompute_fov_map(player)
	
	map.draw(con, FOV)
		
	# Blit contents on the 'con' console to the root console
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	
	
def handle_keys():	
	global FOV, generateMonsters
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
		start_new_map()
	elif key.vk == libtcod.KEY_ESCAPE:
		return "exit"	
	return player.get_input(map, objects)

def start_new_map():		
	del objects[:]
	objects.append(player)
	map.clear(con)
	map.make_map(objects, generateMonsters)
	player.set_position(map.center_of_first_room)
	map.recompute_fov_map(player)
	render_all()

	
start_new_map()	
game_state = "playing"
player_action = None

# Main game loop
while not libtcod.console_is_window_closed():
	# Set the default console window to 'con', this is the main window
	libtcod.console_set_default_foreground(0, libtcod.white)
	
	for obj in objects:
		obj.update(map, objects)
	
	map.update()
	
	render_all()
	
	# Flush changes to the screen (this updates what is visible on-screen)
	libtcod.console_flush()
	
	for obj in objects:
		obj.clear(con)
	
	player_action = handle_keys()
	
	if player_action == "exit":
		break