import libtcodpy as libtcod
from Object import Object
from Player import Player
from Map import Map

# Window dimensions
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

player = Player(25, 23, '@', libtcod.white)
npc = Object(SCREEN_WIDTH / 2 - 5, SCREEN_HEIGHT / 2, '@', libtcod.yellow)
objects = [npc, player]

# Set console font
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_LAYOUT_TCOD)

# Initialize window
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
	
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
map = Map(80, 50)

def render_all():
	for obj in objects:
		obj.draw(con)
		
	map.draw(con)
	
		
	# Blit contents on the 'con' console to the root console
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	
	
def handle_keys():	
	key = libtcod.console_wait_for_keypress(True)
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		# This makes alt + enter toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
		
	if key.vk == libtcod.KEY_ESCAPE:
		return True

# Main game loop
while not libtcod.console_is_window_closed():
	# Set the default console window to 'con', this is the main window
	libtcod.console_set_default_foreground(0, libtcod.white)
	
	for obj in objects:
		obj.update(map, objects)
	
	render_all()
	
	# Flush changes to the screen (this updates what is visible on-screen)
	libtcod.console_flush()
	
	for obj in objects:
		obj.clear(con)
	
	exit = handle_keys()
	if exit:
		break