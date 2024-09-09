import random
import json
import os
import sys
import inspect

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from util import evaluation

# Define constants used in evaluation
WHAT_BEATS = {"r": "p", "p": "s", "s": "r"}
BEATS_WHAT = {"r": "s", "p": "r", "s": "p"}

class BoardGenerator:
    def __init__(self):
        self.piece_types = ['r', 'p', 's']
        self.all_coordinates = [(r, q) for r in range(-4, 5) for q in range(-4, 5) if -4 <= r + q <= 4]
        self.our_side = "lower"  # Default side for generating board states
        self.WHAT_BEATS = WHAT_BEATS
        self.BEATS_WHAT = BEATS_WHAT

    def generate_random_board_state(self):
        lower_throws_left = random.randint(0, 9)
        upper_throws_left = random.randint(0, 9)

        lower_pieces_limit = 9 - lower_throws_left
        upper_pieces_limit = 9 - upper_throws_left

        lower_pieces = {"r": [], "p": [], "s": [], "throws_left": lower_throws_left}
        upper_pieces = {"r": [], "p": [], "s": [], "throws_left": upper_throws_left}
        occupied_coordinates = set()

        def place_pieces(pieces_dict, piece_limit):
            for _ in range(piece_limit):
                piece_type = random.choice(self.piece_types)
                coord = random.choice([c for c in self.all_coordinates if c not in occupied_coordinates])
                pieces_dict[piece_type].append(coord)
                occupied_coordinates.add(coord)

        place_pieces(lower_pieces, lower_pieces_limit)
        place_pieces(upper_pieces, upper_pieces_limit)

        # Calculate the evaluation score using the evaluation function from util.py
        evaluation_score = evaluation(self, lower_pieces, upper_pieces)

        return [[lower_pieces, upper_pieces], evaluation_score]

    def generate_random_board_states(self, num_states):
        board_states = [self.generate_random_board_state() for _ in range(num_states)]
        return board_states

    def save_board_states(self, filename, num_states):
        board_states = self.generate_random_board_states(num_states)
        with open(filename, 'w') as json_file:
            json.dump(board_states, json_file, indent=2)
        print(f"Random board states with evaluation scores have been generated and saved to '{filename}'.")

# Generate the board states
board_generator = BoardGenerator()
file_path = os.path.join(current_dir, 'training_data.json')
board_generator.save_board_states(file_path, 200000)