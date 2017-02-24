import prepare, libtcodpy

class Camera(object):
    def __init__(self):
        self.width, self.height = prepare.SCREEN_WIDTH, prepare.SCREEN_HEIGHT
        self.console = prepare.con
        self.target = None
        self.x, self.y = 0, 0
        
    def flush(self):
        # Flushes the console, updating the display
        libtcodpy.console_flush()