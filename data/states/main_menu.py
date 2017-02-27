from .. import state_machine, menu_helper
import shelve, libtcodpy, os

MENU_BKGND_PATH = os.path.join("resources", "menu_background.png")
MENU_WIDTH = 30

class MainScreen(state_machine._State):
    def __init__(self):
        state_machine._State.__init__(self)
        self.bkgnd_img = libtcodpy.image_load(MENU_BKGND_PATH)
        self.bg_drawn = False
        self.next = "GAME"
        self.state_machine = state_machine.StateMachine()
        self.state_dict =  {"MAIN" : MainMenu(),
                            "QUIT" : QuitGame()}
        self.state_machine.setup_states(self.state_dict, "MAIN")
        
    def update(self, input):
        self.state_machine.update(input)
        if self.state_machine.state.quit:
            self.quit = True
        
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
        self.persist["player"] = self.state_machine.state.persist["player"]
        self.persist["map"] = self.state_machine.state.persist["map"]
        self.persist["log"] = self.state_machine.state.persist["log"]
        return self.persist

class MainMenu(menu_helper.BasicMenu):
    def __init__(self):
        menu_helper.BasicMenu.__init__(self, "", ["Start a new game", "Continue last game", "Quit"], MENU_WIDTH)
        
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
    def __init__(self):
        menu_helper.BasicMenu.__init__(self, "Are you sure you want to quit?", ["No", "Yes"], MENU_WIDTH)
    
    def update(self, input):
        self.get_menu_input(input)
       
        if self.choice_made:
            if self.index == 0:
                self.next = "MAIN"
                self.done = True
            if self.index == 1:
                self.quit = True
    