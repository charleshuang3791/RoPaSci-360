# import code taken from https://gist.github.com/JungeAlexander/6ce0a5213f3af56d7369
import os,sys,inspect
import random

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from util import *

class Player:

	# initialises piece storage data structure
	our_pieces = {'r':[], 'p':[], 's':[], 'throws_left':9}
	their_pieces = {'r':[], 'p':[], 's':[], 'throws_left':9}

	our_side = "unknown"

	# like throws_left, this refers to the number of turns before an action is undertaken
	turns_completed = 0

	# pieces_names_list
	pieces_names_list = ['r', 'p', 's']

	# taken from assignment 1 sample sols
	BEATS_WHAT = {'r': 's', 'p': 'r', 's': 'p'}
	WHAT_BEATS = {'r': 'p', 'p': 's', 's': 'r'}

	def __init__(self, player):
		"""
		Called once at the beginning of a game to initialise this player.
		Set up an internal representation of the game state.

		The parameter player is the string "upper" (if the instance will
		play as Upper), or the string "lower" (if the instance will play
		as Lower).
		"""
		self.our_side = player

	def action(self):
		"""
		Called at the beginning of each turn. Based on the current state
		of the game, select an action to play this turn.
		"""

		# makes first move
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

		# starting our utility matrices tree
		# This is like an accessory to the main tree, helping us calculate the equilibrium sols
		# 0th level: matrix for the current board state, considers immediate next move pair
		# 1st level: matrices for the possible board states 1 move into the future, considers
		# all the move pairs for those board states using the evaluation scores generated from
		# tree 1's second level
		# NOTE: the number of matrices in each level matches up with the number of board states
		# in each level
		# NOTE: scores_tree have one less level than the states_tree
		matrix_rows_num = len(our_moves)
		matrix_cols_num = len(their_moves)
		possible_moves_matrix = np.zeros((matrix_rows_num, matrix_cols_num))

		# starting our board states tree
		# branch level node: [our_moves, their_moves, our_pieces, their_pieces]
		# leaf  level  node: [our_pieces, their_pieces]
		states_tree = []
		nth_level_of_states_tree = []
		node = [our_moves, their_moves, copy_of_our_pieces, copy_of_their_pieces]
		nth_level_of_states_tree.append(node)
		states_tree.append(nth_level_of_states_tree)

		# creating 1st and final level of states_tree
		states_tree = create_leaf_level_for_states_tree(self, states_tree)

		# Apply evaluation function at the leaf nodes
		possible_moves_matrix = fill_matrix_in1(self, possible_moves_matrix, states_tree[-1])

		# cashing in our ultimate moves matrix
		try:
			our_solution = solve_game(possible_moves_matrix, True, True)
			max_sol_value = 0
			for sol_index, solution in enumerate(our_solution[0]):
				if solution > max_sol_value:
					max_sol_value = solution
					max_sol_value_index = sol_index

			golden_move = our_moves[max_sol_value_index]
		except:
			golden_move = our_moves[random.randrange(len(our_moves))]

		return golden_move

	def update(self, opponent_action, player_action):
		"""
		Called at the end of each turn to inform this player of both
		players' chosen actions. Update your internal representation
		of the game state.
		The parameter opponent_action is the opponent's chosen action,
		and player_action is this instance's latest chosen action.
		"""
		updated_positions = give_updated_pieces(self, opponent_action, player_action, self.their_pieces, self.our_pieces)
		self.our_pieces = updated_positions[1]
		self.their_pieces = updated_positions[0]