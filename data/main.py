from . import prepare, tools
from .states import main_menu


def main():
    control = tools.Control()
    state_dict = {"MAINSCREEN" : main_menu.MainScreen()}
    control.state_machine.setup_states(state_dict, "MAINSCREEN")
    control.main()