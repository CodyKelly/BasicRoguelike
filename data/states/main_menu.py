from .. import state_machine, menu_helper
from ..gameobjects import player, map
import shelve, libtcodpy, os

MENU_BKGND_PATH = os.path.join("resources", "menu_background.png")

class MainScreen(state_machine._State):
    def __init__(self):
        state_machine._State.__init__(self)
        self.bkgnd_img = libtcodpy.image_load(MENU_BKGND_PATH)
        self.bg_drawn = False
        self.next = "GAME"
        self.state_machine = state_machine.StateMachine()
        self.state_dict =  {"MAIN" : MainMenu(),
                            "NEW" : NewGame(),
                            "LOAD" : LoadGame(),
                            "QUIT" : QuitGame()}
        self.state_machine.setup_states(self.state_dict, "MAIN")
        
    def update(self, input):
        self.state_machine.update(input)
        if self.state_machine.state.quit:
            if self.state_machine.state_name == "QUIT":
                self.quit = True
            else:
                self.done = True
        
    def draw(self, camera):
        # Blit background image
        libtcodpy.image_blit_2x(self.bkgnd_img, 0, 0, 0)

        # Show the game's title and credits
        libtcodpy.console_set_default_foreground(0, libtcodpy.light_blue)
        libtcodpy.console_print_ex(0, camera.width / 2, camera.height / 2 - 10, libtcodpy.BKGND_NONE, libtcodpy.CENTER, "Roguelike thinger")
        libtcodpy.console_print_ex(0, camera.width / 2, camera.height / 2 - 8, libtcodpy.BKGND_NONE, libtcodpy.CENTER, "Written by Cody Kelly and Roguebasin")
        
        self.state_machine.state.draw(camera)
        
    def cleanup(self):
        self.done = False
        self.state_machine.done = False
        self.persist["player"] = self.state_machine.state.persist["player"]
        self.persist["map"] = self.state_machine.state.persist["map"]
        self.persist["log"] = self.state_machine.state.persist["log"]
        return self.persist
        
class MainMenu(menu_helper.BasicMenu):
    '''
    The main menu.
    Can be expanded to include options for settings, stats, map editor, etc.
    '''
    def __init__(self):
        menu_helper.BasicMenu.__init__(self, "", ["Start a new game", "Continue last game", "Quit"])
        
    def update(self, input):
        self.get_menu_input(input)
        
        if self.choice_made:
            if self.index == 0:
                self.next = "NEW"
            elif self.index == 1:
                self.next = "LOAD"
            elif self.index == 2:
                self.next = "QUIT"
            
            self.done = True
            
class QuitGame(menu_helper.BasicMenu):
    '''
    Asks the user if they're sure about quitting the game
    (Yes its annoying but it may be a necessary evil)
    '''
    def __init__(self):
        menu_helper.BasicMenu.__init__(self, "Are you sure you want to quit?", ["No", "Yes"])
    
    def update(self, input):
        self.get_menu_input(input)
       
        if self.choice_made:
            if self.index == 0:
                self.next = "MAIN"
                self.done = True
            if self.index == 1:
                self.quit = True
    
class NewGame(state_machine._State):
    '''
    Starts a new game
    I'm leaving this as a small state so that it can be expanded later.
    Player name, map settings, character creation can all be done in this state 
    (or its substates..)
    '''
    def __init__(self):
        state_machine._State.__init__(self)
        
    def startup(self, persist):
        self.persist = persist
        self.done = True
        self.persist["player"] = player.Player()
        self.persist["map"] = map.Map()
        self.persist["log"] = []
        
class LoadGame(menu_helper.BasicMenu):
    '''
    Gives the user a list of saved games (or a message saying there are none),
    and loads the one chosen.
    '''
    def __init__(self):
        menu_helper.BasicMenu.__init__(self)
        self.back_text = "Back to the main menu"    # Text for the back button
    
    def startup(self, persist):
        self.persist = persist
        self.files = self.get_save_files()          # A list of all saved games
        self.make_menu()
    
    def update(self, input):
        self.get_menu_input(input)
        
        if self.choice_made:
            # If there weren't any files to choose from, or if the player chose to go back,
            # then we go back to the main menu
            if len(self.files) == 0 or self.options[self.index] == self.back_text:
                self.next = "MAIN"
            else:
                self.load_game()
                
            self.done = True
            
    def make_menu(self):
        if len(self.files) == 0:
            self.set_header("There are no games saved")
        else:
            self.set_header("Please choose a saved game")
        
        # Make a list of all savegames and add an option to go back to the end
        menu_options = self.files
        menu_options.append(self.back_text)
        
        self.set_options(menu_options)
        
    def get_save_files(self):
        files = []
        for file in os.listdir(os.path.join(os.curdir, "saves")):
            if file.endswith(".sav"):
                files.append(file)
                
        return files
        
    def load_game(self):
        file = shelve.load("../../saves/{0}".format(self.options[self.index]))
        self.persist["player"] = file["player"]
        self.persist["map"] = file["map"]
        self.persist["log"] = file["log"]
        file.close()