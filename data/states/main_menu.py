from .. import state_machine, gui
import shelve, libtcodpy, os

MENU_BKGND_PATH = os.path.join("resources", "menu_background.png")
CHOICES = ["NEW", "LOAD", "QUIT"]

class MainMenu(state_machine._State):
    def __init__(self):
        state_machine._State.__init__(self)
        self.bkgnd_img = libtcodpy.image_load(MENU_BKGND_PATH)
        self.bg_drawn = False
        self.next = "GAME"
        
    def update(self, input):
        print(self.bg_drawn)
        if self.bg_drawn:   # If the background hasn't been drawn we need to do that first
                            # Otherwise it won't be at all since the main menu waits
                            # for user input and then continues to the next state
        
            # Show options and wait for the player's choice
            choice = gui.menu(input, "", ["Start a new game", "Continue last game", "Quit"], 24)

            if CHOICES[choice] == "NEW":
                self.start_new_game()
                self.done = True
            elif CHOICES[choice] == "LOAD":
                self.load_last_game()
                self.done = True
            elif CHOICES[choice] == "QUIT":
                self.quit = True
        
    def draw(self, camera):
        # Blit background image
        libtcodpy.image_blit_2x(self.bkgnd_img, 0, 0, 0)

        # Show the game's title and credits
        libtcodpy.console_set_default_foreground(0, libtcodpy.light_blue)
        libtcodpy.console_print_ex(0, camera.width / 2, camera.height / 2 - 6, libtcodpy.BKGND_NONE, libtcodpy.CENTER, "Roguelike thinger")
        libtcodpy.console_print_ex(0, camera.width / 2, camera.height / 2 - 4, libtcodpy.BKGND_NONE, libtcodpy.CENTER, "Written by Cody Kelly and Roguebasin")
        
        self.bg_drawn = True
        
    def start_new_game(self):
        self.persistant_variables["player"] = None
        self.persistant_variables["map"] = None
        self.persistant_variables["log"] = None
        
    def load_last_game(self):
        filePath = os.path.join("saves", "savegame")
        file = shelve.open(filePath)
        
        self.persistant_variables["player"] = file["player"]
        self.persistant_variables["map"]    = file["map"]
        self.persistant_variables["log"]    = file["log"]
        
class _State(object):
    # This is a basic state class, all states should inherit this one
    def __init__(self):
        self.done = False
        self.quit = False
        self.previous_state = None
        self.next_state = None
        self.persistant_variables = {}
        
    def cleanup(self):
        # Set self.done to False for next time this state is used
        self.done = False
        # Give back the persistant variables
        return self.persistant_variables
        
    def startup(self, persistant_variables):
        # Save variables to remember
        self.persistant_variables = persistant_variables
    
    def update(self, input):
        pass
        
    def draw(self, camera):
        pass