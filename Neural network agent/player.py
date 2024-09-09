import inspect
import os
import random
import sys

from keras.models import load_model

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)

sys.path.insert(0, current_dir)
from data_formatter import format_board_state

sys.path.insert(0, parent_dir)
from util import *

class Player:
    our_pieces = {'r':[], 'p':[], 's':[], 'throws_left':9}
    their_pieces = {'r':[], 'p':[], 's':[], 'throws_left':9}
    our_side = "unknown"
    turns_completed = 0
    pieces_names_list = ['r', 'p', 's']
    BEATS_WHAT = {'r': 's', 'p': 'r', 's': 'p'}
    WHAT_BEATS = {'r': 'p', 'p': 's', 's': 'r'}

    def __init__(self, player):
        self.our_side = player
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'trained_model.h5')
        self.model = load_model(model_path)

    def action(self):
        if self.turns_completed == 0:
            piece_to_throw = self.pieces_names_list[random.randrange(3)]
            self.turns_completed += 1
            if self.our_side == "lower":
                return "THROW", piece_to_throw, (-4, 2)
            else:
                return "THROW", piece_to_throw, (4, -2)

        our_moves, their_moves, copy_of_our_pieces, copy_of_their_pieces = give_all_moves(self, copy.deepcopy(self.our_pieces), copy.deepcopy(self.their_pieces))
        if len(our_moves) == 1:
            return our_moves[0]

        board_states = []
        for our_move in our_moves:
            for their_move in their_moves:
                # Simulate the move
                new_our_pieces = copy.deepcopy(copy_of_our_pieces)
                new_their_pieces = copy.deepcopy(copy_of_their_pieces)
                updated_positions = give_updated_pieces(self, their_move, our_move, new_their_pieces, new_our_pieces)
                new_our_pieces, new_their_pieces = updated_positions[1], updated_positions[0]
                score = evaluation(self, new_our_pieces, new_their_pieces)
                board_states.append((score, our_move, new_our_pieces, new_their_pieces))

        # Sort board states by evaluation score and select the top moves
        board_states.sort(reverse=True, key=lambda x: x[0])
        top_board_states = board_states[:min(10, len(board_states))]

        # Apply neural network to the top board states and return the move that leads to the highest score
        max_nn_score = -float('inf')
        best_move = None

        for _, move, our_pieces, their_pieces in top_board_states:
            formatted_board = format_board_state(our_pieces, their_pieces)
            nn_score = self.model.predict(formatted_board.reshape(1, 9, 9, 6))
            
            if self.our_side == "upper":
                nn_score = -nn_score
            
            if nn_score > max_nn_score:
                max_nn_score = nn_score
                best_move = move

        return best_move

    def update(self, opponent_action, player_action):
        updated_positions = give_updated_pieces(self, opponent_action, player_action, self.their_pieces, self.our_pieces)
        self.our_pieces = updated_positions[1]
        self.their_pieces = updated_positions[0]
