from . import prepare, tools
from .states import main_menu


def main():
    control = tools.Control()
    state_dict = {"MAINMENU"   : main_menu.MainMenu()}
    control.state_machine.setup_states(state_dict, "MAINMENU")
    control.main()