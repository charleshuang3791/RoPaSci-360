# main.py

import importlib.util

from referee.log import config, print, _print, comment
from referee.game import Game, _RENDER, COLOURS, _FORMAT_ACTION
from referee.player import PlayerWrapper, set_space_line
from battleground.options import get_options

def load_player_class(player_file):
    """Dynamically load the Player class from the provided Python file."""
    spec = importlib.util.spec_from_file_location("Player", player_file)
    player_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(player_module)
    return player_module.Player

def main():
    options = get_options()

    # Create a star-log for controlling the format of output from within this program
    out = config(level=options.verbosity)
    comment("all messages printed by the client after this begin with a *")
    comment("(any other lines of output must be from your Player class).")
    comment()

    try:
        # Load player classes from the specified files
        Player1 = load_player_class(options.player1_file)
        Player2 = load_player_class(options.player2_file)

        # Initialize players without using PlayerWrapper, directly
        p1 = Player1("upper")
        p2 = Player2("lower")

        # Even though we're not limiting space, the display
        # may still be useful for some users
        set_space_line()

        # Simulate the game locally
        result = play_local_game(p1, p2, log_filename=options.logfile, 
                                 print_state=(options.verbosity > 1), 
                                 use_debugboard=(options.verbosity > 2))
        comment("game over!", depth=-1)
        print(result)
    except KeyboardInterrupt:
        _print()  # (end the line)
        comment("bye!")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def play_local_game(p1, p2, log_filename=None, print_state=True, use_debugboard=False):
    """Play a game between two local players."""
    if print_state:
        def display_state(game):
            comment("displaying game info:")
            comment(
                _RENDER(
                    game,
                    use_debugboard=use_debugboard,
                ),
                depth=1,
            )
    else:
        def display_state(game):
            pass

    # Set up a new game and initialize the players
    game = Game(log_filename=log_filename)
    comment("initializing players", depth=-1)

    # Display the initial state of the game
    comment("game start!", depth=-1)
    display_state(game)

    turn = 1
    while not game.over():
        comment(f"Turn {turn}", depth=-1)

        # Ask both players for their next action (calling .action() methods)
        action_1 = p1.action()
        action_2 = p2.action()

        # Validate both actions and apply them to the game if they are allowed
        game.update(action_1, action_2)
        display_state(game)

        # Notify both players of the actions (via .update() methods)
        p1.update(opponent_action=action_2, player_action=action_1)
        p2.update(opponent_action=action_1, player_action=action_2)

        turn += 1

    return game.end()
