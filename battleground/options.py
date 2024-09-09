# options.py

import sys
import argparse

# No need to import battleground.protocol anymore

# Program information:
PROGRAM = "battleground"
VERSION = "2021.1.0"
DESCRIP = "play a local game between two Player classes!"

WELCOME = f"""***************************************************************
Welcome to {PROGRAM} version {VERSION}.

{DESCRIP}

Run `python -m battleground -h` for additional usage information.
***************************************************************"""

def get_options():
    """
    Parse and return command-line arguments for local play.
    """

    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=DESCRIP,
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # positional arguments for player files
    positionals = parser.add_argument_group(
        title="player Python file locations"
    )
    positionals.add_argument(
        "player1_file",
        metavar="player1",
        help="path to the first player's Python file",
    )
    positionals.add_argument(
        "player2_file",
        metavar="player2",
        help="path to the second player's Python file",
    )

    # optional arguments used for configuration:
    optionals = parser.add_argument_group(title="optional arguments")
    optionals.add_argument(
        "-h",
        "--help",
        action="help",
        help="show this message",
    )
    optionals.add_argument(
        "-V",
        "--version",
        action="version",
        version=VERSION,
    )
    optionals.add_argument(
        "-v",
        "--verbosity",
        type=int,
        choices=range(0, 4),
        nargs="?",
        default=2,
        const=3,
        help="control the level of output (not including output from players).",
    )

    optionals.add_argument(
        "-l",
        "--logfile",
        metavar="LOGFILE",
        type=str,
        nargs="?",
        default=None,
        const="game.log",
        help="if you supply this flag the client will create a log of "
        "all game actions in a text file named %(metavar)s "
        "(default: %(const)s)",
    )

    args = parser.parse_args()

    if args.verbosity > 0:
        print(WELCOME)

    return args
