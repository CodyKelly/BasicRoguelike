import libtcodpy, prepare, state_machine

class BasicMenu(state_machine._State):
    def __init__(self, header, options, width, bg_transparency=0.7, fg_transparency=1.0):
        state_machine._State.__init__(self)
        self.header = header
        self.options = options
        self.width = width
        self.choice_made = False
        
        # Foreground and background transparencies
        self.bg_transparency = bg_transparency
        self.fg_transparency = fg_transparency
        
        # The index of the currently highlighted menu option
        self.index = 0
        
        self.make_window()
    
    def update(self, input):
        self.get_menu_input(input)
        
    def draw(self, camera):
        self.draw_window()
        
    def get_menu_input(self, input):
        key, mouse = input["key"], input["mouse"]
        
        if mouse.lbutton:
            (menu_x, menu_y) = (mouse.cx - self.x_offset, (mouse.cy - self.y_offset) / 2)
            
            if menu_x >= 0 and menu_x < self.width and menu_y >= 0 and menu_y < self.height - self.header_height:
                self.index = menu_y
                
        if mouse.lbutton_pressed:
            (menu_x, menu_y) = (mouse.cx - self.x_offset, (mouse.cy - self.y_offset) / 2)
            
            if menu_x >= 0 and menu_x < self.width and menu_y >= 0 and menu_y < self.height - self.header_height:
                self.choice_made = True
                self.index = menu_y
        
        # Move selection up or down
        if key.vk == libtcodpy.KEY_DOWN:
            self.index = (self.index + 1) % len(self.options)
        elif key.vk == libtcodpy.KEY_UP:
            self.index = (self.index - 1) % len(self.options)
        elif key.vk == libtcodpy.KEY_ENTER:
            self.choice_made = True
        
    def draw_window(self):
        self.print_header()
        self.print_options()
        self.highlight_index()
        libtcodpy.console_blit(self.window, 0, 0, self.width, self.height, 0, self.x, self.y, self.fg_transparency, self.bg_transparency)
        libtcodpy.console_clear(self.window)
        
    def highlight_index(self):
        # Highlights the option at self.index
        y = self.index * 2 + self.header_height + 1
        
        for x in range(0, self.width):
            libtcodpy.console_set_char_background(self.window, x, y, libtcodpy.white, libtcodpy.BKGND_SET)
            libtcodpy.console_set_char_foreground(self.window, x, y, libtcodpy.black)
        
    def print_header(self):
        # Prints the header onto self.window (with auto-wrap)
        libtcodpy.console_print_rect_ex(self.window, 0, 0, self.width, self.height, libtcodpy.BKGND_NONE, libtcodpy.LEFT, self.header)
        
    def print_options(self):
        # Prints all the options onto self.window
        y = self.header_height
        for option_text in self.options:
            for x in range(0, self.width):
                libtcodpy.console_set_char_background(self.window, x, y, libtcodpy.white, libtcodpy.BKGND_SET)
            y += 1
            libtcodpy.console_print_ex(self.window, 0, y, libtcodpy.BKGND_NONE, libtcodpy.LEFT, option_text)
            y += 1
        
        y + 1
        for x in range(0, self.width):
            libtcodpy.console_set_char_background(self.window, x, y, libtcodpy.white, libtcodpy.BKGND_SET)
        
    def make_window(self):
        # Dimensions of the menu
        self.header_height = self.calculate_header_height()
        self.height = self.header_height + len(self.options) * 2 + 1
        
        # An offscreen console to draw to
        self.window = libtcodpy.console_new(self.width, self.height)
        
        # Position of the menu within the main console
        self.x = prepare.SCREEN_WIDTH / 2 - self.width / 2
        self.y = prepare.SCREEN_HEIGHT / 2 - self.height / 2
        
        # Coordinates of the menu, excluding the header
        self.x_offset = self.x
        self.y_offset = self.y + self.header_height
    
    def calculate_header_height(self):
        if self.header == "":
            return 0
        
        return libtcodpy.console_get_height_rect(prepare.console, 0, 0, self.width, prepare.SCREEN_HEIGHT, self.header)
        
    def set_header(self, header):
        self.header = header
        self.make_window()
        
    def set_options(self, options):
        self.options = options
        self.make_window()
        
    def cleanup(self):
        self.index = 0
        self.done = False
        self.choice_made = False
        return self.persist