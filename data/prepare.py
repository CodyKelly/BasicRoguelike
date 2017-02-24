'''
Here we'll define some global variables and initialize libtcodpy for use
'''

import libtcodpy, os

# Window dimensions
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

# Libtcodpy initialization
#print(os.path.join('resources', 'arial12x12.png'))
libtcodpy.console_set_custom_font(os.path.join('resources', 'arial12x12.png'), libtcodpy.FONT_LAYOUT_TCOD)  # Set console font
libtcodpy.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Roguelike', False)                # Initialize window

console = libtcodpy.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)    # Main console