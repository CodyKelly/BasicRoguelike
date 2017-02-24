class StateMachine(object):
    def __init__(self):
        self.state_dict = {}    # This is a dictionary of states, holding the name of every state in the game and the states themselves.
        self.state = None       # This is our current state, which we will update and render every frame
        self.state_name = None  # This holds the name of our current state
        self.done = False       # This flag will tell the rest of our program that the state machine is no longer running, and we'll therefore shut down our game
        
    def setup_states(self, state_dict, start_state):
        # Gets a dictionary of states, and sets the specified "start_state" as the current state
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        
    def update(self, input):
        # Update current state with the current input
        if self.state:
            self.state.update(input)
        
        # Check to see if the state is requesting a program exit
        if self.state.quit:
            self.done = True
        # If not, see if the state is done executing
        elif self.state.done:
            self.change_state()
    
    def draw(self, camera):
        self.state.draw(camera)
        
    def change_state(self):
        # When the current state is done executing, we'll first call its cleanup function to get any variables it needs to remember (persistant_variables).
        # Then we switch to a new state and have that new state set up and remember the variables
        
        # Store current state name as the previous and the next state name as the current's
        previous_state = self.state_name
        self.state_name = self.state.next
        
        # Keep any variables we want to remember while also cleaning up the current state
        persistant_variables = self.state.cleanup()
        
        # Change the current state and call its startup function, while also giving it any persistant variables
        self.state = self.state_dict[self.state_name]
        self.state.startup(persistant_variables)
        
        # And set the (now current) state's previous state
        self.state.previous_state = previous_state
        
    def get_event(self, events):
        pass
        
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