import libtcodpy, state_machine, map

class Game(state_machine._State):
    def __init__(self):
        state_machine._State.__init__(self)
        self.next = "PAUSE"
    
    def startup(self, persist):
        # Get player, map, and game log
        self.persist    = persist
        self.player     = persist["player"]
        self.map        = persist["map"]
        self.log        = persist["log"]