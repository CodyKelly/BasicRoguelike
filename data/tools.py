import libtcodpy, state_machine, prepare

FPS_CAP = 60

class Control(object):
    def __init__(self):
        self.caption = "Noirland"
        self.camera = Camera()
        self.state_machine = state_machine.StateMachine()
        self.done = False
        self.input = {"key"     : libtcodpy.Key(), 
                      "mouse"   : libtcodpy.Mouse()}
    
    def update(self):
        libtcodpy.sys_check_for_event(libtcodpy.EVENT_KEY_PRESS | libtcodpy.EVENT_MOUSE, self.input["key"], self.input["mouse"])
        key = self.input["key"]
        
        self.check_for_exit(key)
        self.check_for_fullscreen(key)
        
        self.state_machine.update(self.input)
        
    def draw(self):
        if not self.state_machine.state.done:
            self.state_machine.draw(self.camera)
        self.camera.flush()
        
    def main(self):
        while not self.done:
            self.update()
            self.draw()

    def check_for_exit(self, key):
        escape_pressed = key.vk == libtcodpy.KEY_ESCAPE
        
        if self.state_machine.done or escape_pressed or libtcodpy.console_is_window_closed():
            self.done = True
            
    def check_for_fullscreen(self, key):
        if key.vk == libtcodpy.KEY_ENTER and (key.lalt or key.ralt):
            libtcodpy.console_set_fullscreen(not libtcodpy.console_is_fullscreen())
            
class Camera(object):
    def __init__(self):
        self.width, self.height = prepare.SCREEN_WIDTH, prepare.SCREEN_HEIGHT
        self.console = prepare.console
        self.target = None
        self.x, self.y = 0, 0
        
    def flush(self):
        # Flushes the console, updating the display
        libtcodpy.console_flush()
        
