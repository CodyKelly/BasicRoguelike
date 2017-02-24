import libtcodpy, state_machine, prepare

FPS_CAP = 60

class Control(object):
    def __init__(self):
        self.caption = "Noirland"
        self.camera = Camera()
        self.state_machine = state_machine.StateMachine()
        self.done = False
        self.input = {"Key"     : libtcodpy.Key(), 
                      "Mouse"   : libtcodpy.Mouse()}
    
    def update(self):
        # Checks for input and sends the input to the state_machine
        libtcodpy.sys_check_for_event(libtcodpy.EVENT_KEY_PRESS | libtcodpy.EVENT_MOUSE, self.input["Key"], self.input["Mouse"])
        self.state_machine.update(self.input)
        
        self.done = self.state_machine.done
        
    def draw(self):
        if not self.state_machine.state.done:
            self.state_machine.draw(self.camera)
        self.camera.flush()
        
    def main(self):
        while not self.done:
            self.update()
            self.draw()
            
    def event_loop(self):
        if self.input["Key"].vk == libtcodpy.KEY_ESCAPE:
            self.done = True

class Camera(object):
    def __init__(self):
        self.width, self.height = prepare.SCREEN_WIDTH, prepare.SCREEN_HEIGHT
        self.console = prepare.console
        self.target = None
        self.x, self.y = 0, 0
        
    def flush(self):
        # Flushes the console, updating the display
        libtcodpy.console_flush()
        
