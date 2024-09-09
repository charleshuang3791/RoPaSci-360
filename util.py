import math
import numpy as np
import scipy.optimize as opt
import copy

def give_updated_pieces(self, enemy_action, friendly_action, enemy_pieces, friendly_pieces):
	"""
	Returns a list of the updated pieces positions:
	[updated enemy_pieces, updated friendly_pieces]
	"""

	# first update the enemy pieces
	enemy_pieces = update_first_stage(enemy_action, enemy_pieces)

	# then update the friendly pieces
	friendly_pieces = update_first_stage(friendly_action, friendly_pieces)

	# checks which pieces need to be removed
	attacking_pieces_coords_r = []
	attacking_pieces_coords_p = []
	attacking_pieces_coords_s = []

	for element in friendly_pieces['r']:
		attacking_pieces_coords_r.append(element)
	for element in enemy_pieces['r']:
		attacking_pieces_coords_r.append(element)
	for element in friendly_pieces['p']:
		attacking_pieces_coords_p.append(element)
	for element in enemy_pieces['p']:
		attacking_pieces_coords_p.append(element)
	for element in friendly_pieces['s']:
		attacking_pieces_coords_s.append(element)
	for element in enemy_pieces['s']:
		attacking_pieces_coords_s.append(element)

	defeated_pieces_r = []
	defeated_pieces_p = []
	defeated_pieces_s = []

	# check if any upper pieces have been defeated
	for piece_type in self.pieces_names_list:
		for coord in friendly_pieces[piece_type]:
			if piece_type == 'r':
				if coord in attacking_pieces_coords_p:
					defeated_pieces_r.append(coord)
			if piece_type == 'p':
				if coord in attacking_pieces_coords_s:
					defeated_pieces_p.append(coord)
			if piece_type == 's':
				if coord in attacking_pieces_coords_r:
					defeated_pieces_s.append(coord)

	# update new defeated pieces and remove from available upper tokens                   
	for piece_type in self.pieces_names_list:
		for _ in friendly_pieces[piece_type]:
			if piece_type == 'r':
				defeated_pieces = defeated_pieces_r
			if piece_type == 'p':
				defeated_pieces = defeated_pieces_p
			if piece_type == 's':
				defeated_pieces = defeated_pieces_s

			for element in defeated_pieces:
				while element in friendly_pieces[piece_type]:
					friendly_pieces[piece_type].remove(element)

	defeated_pieces_r = []
	defeated_pieces_p = []
	defeated_pieces_s = []

	# check if any lower pieces have been defeated                  
	for piece_type in self.pieces_names_list:
		for coord in enemy_pieces[piece_type]:
			if piece_type == 'r':
				if coord in attacking_pieces_coords_p:
					defeated_pieces_r.append(coord)
			if piece_type == 'p':
				if coord in attacking_pieces_coords_s:
					defeated_pieces_p.append(coord)
			if piece_type == 's':
				if coord in attacking_pieces_coords_r:
					defeated_pieces_s.append(coord)

	# update new defeated pieces and remove from available lower tokens
	for piece_type in self.pieces_names_list:
		for _ in enemy_pieces[piece_type]:
			if piece_type == 'r':
				defeated_pieces = defeated_pieces_r
			if piece_type == 'p':
				defeated_pieces = defeated_pieces_p
			if piece_type == 's':
				defeated_pieces = defeated_pieces_s

			for element in defeated_pieces:
				while element in enemy_pieces[piece_type]:
					enemy_pieces[piece_type].remove(element)

	return [enemy_pieces, friendly_pieces]

def update_first_stage(action, pieces):
	if action[0] == "THROW":
		pieces[action[1]].append(action[2])
		pieces['throws_left'] -= 1
	else:
		old_coord = action[1]
		new_coord = action[2] 
		for piece_type in pieces:
			if piece_type != 'throws_left':
				for line_index, coord in enumerate(pieces[piece_type]):
					if coord == old_coord:
						pieces[piece_type][line_index] = new_coord
						break
	return pieces
				
def evaluation(self, our_pieces, their_pieces):
	our_pieces_num = give_pieces_num(our_pieces)
	their_pieces_num = give_pieces_num(their_pieces)
	our_throws_left = our_pieces['throws_left']
	their_throws_left = their_pieces['throws_left']

	# what percentage of the total pieces are ours?
	our_pieces_percentage = our_pieces_num / max(our_pieces_num + their_pieces_num, 1)

	if our_pieces_percentage == 1 and their_throws_left == 0:
		return math.inf

	# what percentage of the total throws are ours?
	our_throws_percentage = our_throws_left / max(our_throws_left + their_throws_left, 1)

	# what percentage of our pieces are in the red zone (able to be thrown on)?
	our_total_list = give_all_pieces_coords_list(our_pieces)
	their_total_list = give_all_pieces_coords_list(their_pieces)

	their_critical_number = their_throws_left - 5
	our_critical_number = our_throws_left - 5

	our_throw_endangered_pieces = give_throw_endangered_pieces(self, our_total_list, their_critical_number)
	their_throw_endangered_pieces = give_throw_endangered_pieces(self, their_total_list, our_critical_number)

	our_throw_endangered_percentage = len(our_throw_endangered_pieces) / max(len(our_throw_endangered_pieces) + len(their_throw_endangered_pieces), 1)

	# what percentage: how many opposition pieces do our current pieces threaten?
	# the same opposition piece being threatened by multiple of our pieces, such duplicate
	# instances are all counted
	our_attacks = give_attacks_for_all_pieces(self, our_pieces, their_pieces)
	their_attacks = give_attacks_for_all_pieces(self, their_pieces, our_pieces)

	our_attack_percentage = len(our_attacks) / max(len(our_attacks) + len(their_attacks), 1)

	# strategy: boards where all enemy piece types have a dominant friendly type on the board are preferred over ones that do not
	corresponding_pieces_present = 0.8
	for piece_type in their_pieces:
		if piece_type == 'throws_left':
			break
		if their_pieces[piece_type]:    
			corresponding_type = self.WHAT_BEATS[piece_type]
			if not our_pieces[corresponding_type]:
				corresponding_pieces_present -= 0.4

	# strategy: pieces that are closer to defeatable enemy tokens are scored higher
	dist_to_defeatable_piece = 20
	for piece_type in our_pieces:
		if piece_type == 'throws_left':
			break
		for our_coord in our_pieces[piece_type]:
			for their_coord in their_pieces[self.BEATS_WHAT[piece_type]]:
				if hex_dist(our_coord, their_coord) < dist_to_defeatable_piece:
					dist_to_defeatable_piece = hex_dist(our_coord, their_coord)
	mindist_to_defeatable_piece = (9 - dist_to_defeatable_piece) / 9         

	return our_pieces_percentage + 0.9*our_throws_percentage - 0.4*our_throw_endangered_percentage + 0.8*our_attack_percentage + corresponding_pieces_present + 0.4*mindist_to_defeatable_piece

def give_pieces_num(pieces):
	num = 0
	values = pieces.values()
	values2 = []
	for value in values:
		if not isinstance(value, int):
			values2.append(value)

	for pieces_list in values2:
		num = num + len(pieces_list)
	return num

def give_pieces_nums(pieces):
	nums = {}

	for piece_type in pieces:
		if piece_type != "throws_left":
			nums[piece_type] = len(pieces[piece_type])
	return nums

def give_least_populous_piece(nums):
	return min(nums.items(), key=lambda x: x[1])[0]

def give_all_pieces_coords_list(pieces):
	total_list = []
	values = pieces.values()
	values2 = []
	for value in values:
		if not isinstance(value, int):
			values2.append(value)

	for pieces_list in values2:
		total_list.extend(pieces_list)
	return total_list

def give_throw_endangered_pieces(self, total_list, critical_number):
	endangered_pieces = []

	for coord in total_list:
		if (self.our_side == "lower" and coord[0] >= critical_number) or \
		   (self.our_side == "upper" and coord[0] <= critical_number):
			endangered_pieces.append(coord)

	return endangered_pieces

def give_possible_moves_for_1_piece(old_coord, friendly_pieces):
	all_points = surrounding_points(old_coord)
	surround_points = all_points.copy()
	for point_list in friendly_pieces.values():
		if not isinstance(point_list, int):
			for point in point_list:
				for surround in surround_points:

					#Swing move is valid
					if point[0] == surround[0] and point[1] == surround[1]:
						all_points += surrounding_points(point)
	# removing all points that are outside the board
	# we want the rows and columns to be between -4 and 4 and for the absolute value of the sum of the coords to be less than or equal to 4
	all_points = [i for i in all_points if (-4 <= i[0] <= 4 and -4 <= i[1] <= 4 and abs(i[0] + i[1]) <= 4)]

	#remove duplicates
	all_points2 = []
	for i in all_points:
		if i not in all_points2:
			all_points2.append(i)

	#Remove old_coord     
	if old_coord in all_points2:
		all_points2.remove(old_coord)

	return all_points2

def surrounding_points(old_coord):
	return [add_tuples(old_coord, (0, 1)), add_tuples(old_coord, (-1, 1)), add_tuples(old_coord, (-1, 0)), add_tuples(old_coord, (0, -1)), add_tuples(old_coord, (1, -1)), add_tuples(old_coord, (1, 0))]

def give_attacks_for_1_piece(self, piece_type, possible_moves, target_pieces):
	attacks = []
	targets = target_pieces[self.BEATS_WHAT[piece_type]]
	for possible_move in possible_moves:
		if possible_move in targets:
			attacks.append(possible_move)

	return attacks

def give_attacks_for_all_pieces(self, attacker_pieces, target_pieces):
	all_attacks = []
	for piece_type in attacker_pieces:
		if piece_type != 'throws_left':
			for line_index, coord in enumerate(attacker_pieces[piece_type]):
				possible_moves = give_possible_moves_for_1_piece(coord, attacker_pieces)
				possible_attacks = give_attacks_for_1_piece(self, piece_type, possible_moves, target_pieces)
				for possible_attack in possible_attacks:
					all_attacks.append(((piece_type, line_index), possible_attack))

	return all_attacks

def surrounding_points_in_board(coord):
	adjacent_points = surrounding_points(coord)
	return [i for i in adjacent_points if (-4 <= i[0] <= 4 and -4 <= i[1] <= 4 and abs(i[0] + i[1]) <= 4)]


def give_reasonable_throws(self, friendly_pieces, enemy_pieces):
	# reasonable throws are: on defeatable pieces, around defeatable pieces
	reasonable_throws = []

	if friendly_pieces['throws_left'] == 0:
		return reasonable_throws

	friendly_pieces_num = give_pieces_num(friendly_pieces)
	enemy_pieces_num = give_pieces_num(enemy_pieces)

	# what percentage of the total pieces are friendly?
	friendly_pieces_percentage = friendly_pieces_num / max(friendly_pieces_num + enemy_pieces_num, 1)

	# strategy: if there are enemy types on board that do not have friendly pieces of a dominant type, throw that
	for piece_type in enemy_pieces:
		if piece_type == 'throws_left':
			break
		desired_type = self.WHAT_BEATS[piece_type]
		if enemy_pieces[piece_type]:
			coord = enemy_pieces[piece_type][0]
			if not friendly_pieces[desired_type]:
				if (self.our_side == "lower" and coord[0] <= 5 - friendly_pieces['throws_left']) or \
				   (self.our_side == "upper" and coord[0] >= friendly_pieces['throws_left'] - 5):
					reasonable_throws.append(("THROW", desired_type, coord))
					return reasonable_throws
				else:
					if self.our_side == "lower":
						coord = (5 - friendly_pieces['throws_left'], -2)
					else:
						coord = (friendly_pieces['throws_left'] - 5, -2)
					adj_coords = surrounding_points_in_board(coord)
					match = 0
					for coord in adj_coords:
						if (self.our_side == "lower" and coord[0] <= 5 - friendly_pieces['throws_left']) or \
						   (self.our_side == "upper" and coord[0] >= friendly_pieces['throws_left'] - 5):
							for piece_type in enemy_pieces:
								if piece_type == 'throws_left':
									break
								for enemy_coord in enemy_pieces[piece_type]:
									if enemy_coord == coord:
										match = 1
										break
								if match == 1:
									break
							if match == 0:
								reasonable_throws.append(("THROW", desired_type, coord))
								return reasonable_throws

	if friendly_pieces['throws_left'] >= 9:
		desired_type = 's'
		for piece_type in enemy_pieces:
			if piece_type != 'throws_left':
				if enemy_pieces[piece_type]:
					desired_type = self.WHAT_BEATS[piece_type]
		reasonable_throws.append(("THROW", desired_type, (-4, 3)))

	# strategy: throw least populous piece next to the furthest friendly piece of a different type
	if friendly_pieces_percentage < 0.51:
		friendly_pieces_nums = give_pieces_nums(friendly_pieces)
		desired_type = give_least_populous_piece(friendly_pieces_nums)
		for piece_type in friendly_pieces:
			if (piece_type != 'throws_left') and (piece_type != desired_type):
				for coord in friendly_pieces[piece_type]:
					adjacent_points = surrounding_points_in_board(coord)
					# iterate through coords surrounding each target
					for adj_coord in adjacent_points:
						if (self.our_side == "lower" and adj_coord[0] <= 5 - friendly_pieces['throws_left']) or \
						   (self.our_side == "upper" and adj_coord[0] >= friendly_pieces['throws_left'] - 5):
							danger = 0
							new_adjacent_points = surrounding_points_in_board(adj_coord)

							# if there are no enemy pieces surrounding the adjacent location, then the throw is reasonable
							for check_point in new_adjacent_points:
								for piece_type in enemy_pieces:
									if piece_type != 'throws_left':
										if check_point in enemy_pieces[piece_type]:
											danger = 1
											break
							if danger == 0:
								reasonable_throws.append(("THROW", desired_type, adj_coord))

	# strategy: throw on top of defeatable enemy pieces
	for piece_type in enemy_pieces:
		if piece_type != 'throws_left':
			for coord in enemy_pieces[piece_type]:
				if (self.our_side == "lower" and coord[0] <= 5 - friendly_pieces['throws_left']) or \
				   (self.our_side == "upper" and coord[0] >= friendly_pieces['throws_left'] - 5):
					# reasonable throw on top of an enemy piece
					desired_type = self.WHAT_BEATS[piece_type]
					reasonable_throws.append(("THROW", desired_type, coord))

	return reasonable_throws


def hex_dist(point1, point2):
	xdiff = point1[0] - point2[0]
	ydiff = point1[1] - point2[1]
	diff = xdiff + ydiff
	return max(abs(xdiff), abs(ydiff), abs(diff))

def solve_game(V, maximiser=True, rowplayer=True):
	"""
	Given a utility matrix V for a zero-sum game, compute a mixed-strategy
	security strategy/Nash equilibrium solution along with the bound on the
	expected value of the game to the player.
	By default, assume the player is the MAXIMISER and chooses the ROW of V,
	and the opponent is the MINIMISER choosing the COLUMN. Use the flags to
	change this behaviour.

	Parameters
	----------
	* V: (n, m)-array or array-like; utility/payoff matrix;
	* maximiser: bool (default True); compute strategy for the maximiser.
		Set False to play as the minimiser.
	* rowplayer: bool (default True); compute strategy for the row-chooser.
		Set False to play as the column-chooser.

	Returns
	-------
	* s: (n,)-array; probability vector; an equilibrium mixed strategy over
		the rows (or columns) ensuring expected value v.
	* v: float; mixed security level / guaranteed minimum (or maximum)
		expected value of the equilibrium mixed strategy.

	Exceptions
	----------
	* OptimisationError: If the optimisation reports failure. The message
		from the optimiser will accompany this exception.
	"""
	V = np.asarray(V)
	# lprog will solve for the column-maximiser
	if rowplayer:
		V = V.T
	if not maximiser:
		V = -V
	m, n = V.shape
	# ensure positive
	c = -V.min() + 1
	Vpos = V + c
	# solve linear program
	res = opt.linprog(
		np.ones(n),
		A_ub=-Vpos,
		b_ub=-np.ones(m),
	)
	if res.status:
		raise OptimisationError(res.message) # TODO: propagate whole result
	# compute strategy and value
	v = 1 / res.x.sum()
	s = res.x * v
	v = v - c # re-scale
	if not maximiser:
		v = -v
	return s, v

def give_moves_for_existing_pieces(pieces):
	moves_worth_considering = []

	for piece_type in pieces:
		if piece_type != 'throws_left':
			for line_index, coord in enumerate(pieces[piece_type]):
				possible_moves_for_this_piece = give_possible_moves_for_1_piece(coord, pieces)
				for possible_move in possible_moves_for_this_piece:
					if hex_dist(coord, possible_move) <= 1:
						move_type = "SLIDE"
					else:
						move_type = "SWING"
					moves_worth_considering.append((move_type, coord, possible_move))

	return moves_worth_considering

def add_tuples(tuple1, tuple2):
	return tuple(map(lambda x, y: x + y, tuple1, tuple2))

def create_leaf_level_for_states_tree(self, states_tree):
	nth_level_of_states_tree = []
	level_above = states_tree[-1]

	for parent in level_above:
		temp_our_moves = parent[0]
		temp_their_moves = parent[1]
		temp_our_pieces = parent[2]
		temp_their_pieces = parent[3]

		for our_move in temp_our_moves:
			for their_move in temp_their_moves:
				temp_updated_pieces = give_updated_pieces(self, their_move, our_move, copy.deepcopy(temp_their_pieces), copy.deepcopy(temp_our_pieces))
				temp_our_new_pieces = temp_updated_pieces[1]
				temp_their_new_pieces = temp_updated_pieces[0]
				node = [temp_our_new_pieces, temp_their_new_pieces]
				nth_level_of_states_tree.append(node)
				
	states_tree.append(nth_level_of_states_tree)

	return states_tree

def fill_matrix_in1(self, possible_moves_matrix, children_nodes_from_states_tree):
	"""
	:param possible_moves_matrix: A numpy matrix where the scores will be inserted.
	:param children_nodes_from_states_tree: A list of children nodes from the states tree, each having elements to be evaluated.
	:return: The updated possible_moves_matrix with scores filled in.
	"""
	# initialise the variables for tracking where to insert our scores
	row_index = 0
	col_index = 0
	current_matrix_rows = np.shape(possible_moves_matrix)[0]
	current_matrix_cols = np.shape(possible_moves_matrix)[1]
	for node in children_nodes_from_states_tree:
		# insert score
		possible_moves_matrix[row_index, col_index] = evaluation(self, node[0], node[1])
		if col_index != current_matrix_cols - 1:
			col_index += 1
		else:
			row_index += 1
			col_index = 0

	return possible_moves_matrix

def fill_matrix_in2(self, possible_moves_matrix, children_nodes_from_scores_tree):
	"""
	:param possible_moves_matrix: A numpy matrix representing the possible moves, where expanded nodes are marked with NaN.
	:param children_nodes_from_scores_tree: A list of child nodes derived from the scores tree.
	:return: The updated possible_moves_matrix with filled values.
	"""
	current_matrix_rows = np.shape(possible_moves_matrix)[0]
	current_matrix_cols = np.shape(possible_moves_matrix)[1]

	row_index = 0
	col_index = 0
	child_index = 0
	
	# some_equil_score = np.nan
	some_equil_score_found = False
	while child_index < len(children_nodes_from_scores_tree):
		if np.isnan(possible_moves_matrix[row_index, col_index]): # means the node was expanded
			node = children_nodes_from_scores_tree[child_index]
			try:
				some_equil_score = solve_game(node, True, True)[1]
				some_equil_score_found = True
			except:
				pass

			child_index += 1

		if some_equil_score_found:
			break

		if col_index != current_matrix_cols - 1:
			col_index += 1
		else:
			row_index += 1
			col_index = 0

	if not some_equil_score_found:
		some_equil_score = 1.5


	row_index = 0
	col_index = 0
	child_index = 0

	largest_equil_score_row_index = self.largest_equil_score_index[0]
	largest_equil_score_col_index = self.largest_equil_score_index[1]
	largest_equil_score_found = False
	while child_index < len(children_nodes_from_scores_tree):
		if np.isnan(possible_moves_matrix[row_index, col_index]): # means the node was expanded
			node = children_nodes_from_scores_tree[child_index]
			if row_index == largest_equil_score_row_index and col_index == largest_equil_score_col_index:
				try:
					largest_equil_score = solve_game(node, True, True)[1]
				except:
					largest_equil_score = some_equil_score

				largest_equil_score_found = True

			child_index += 1

		if largest_equil_score_found:
			break

		if col_index != current_matrix_cols - 1:
			col_index += 1
		else:
			row_index += 1
			col_index = 0


	row_index = 0
	col_index = 0
	child_index = 0

	while child_index < len(children_nodes_from_scores_tree):
		if np.isnan(possible_moves_matrix[row_index, col_index]): # means the node was expanded
			node = children_nodes_from_scores_tree[child_index]
			try:
				possible_moves_matrix[row_index, col_index] = solve_game(node, True, True)[1]
			except:
				possible_moves_matrix[row_index, col_index] = 3 # 3 so that it doesn't get completely blown out of proportion

			child_index += 1
		else:
			possible_moves_matrix[row_index, col_index] = possible_moves_matrix[row_index, col_index] * largest_equil_score

		if col_index != current_matrix_cols - 1:
			col_index += 1
		else:
			row_index += 1
			col_index = 0

	return possible_moves_matrix

def give_all_moves(self, copy_of_our_pieces, copy_of_their_pieces):
	# adding throws worth considering part 1
	our_reasonable_throws = give_reasonable_throws(self, copy_of_our_pieces, copy_of_their_pieces)
	if len(our_reasonable_throws) == 1:
		return our_reasonable_throws, [], copy_of_our_pieces, copy_of_their_pieces

	# adding moves for pieces already on the board
	our_moves = give_moves_for_existing_pieces(copy_of_our_pieces)
	their_moves = give_moves_for_existing_pieces(copy_of_their_pieces)

	# adding throws worth considering part 2
	our_moves.extend(our_reasonable_throws)

	their_moves.extend(give_reasonable_throws(self, copy_of_their_pieces, copy_of_our_pieces))

	return our_moves, their_moves, copy_of_our_pieces, copy_of_their_pieces


# taken from https://stackoverflow.com/questions/23981553/get-all-values-from-nested-dictionaries-in-python
def give_values_of_nested_dict(d):
	for v in d.values():
		if isinstance(v, dict):
			yield from give_values_of_nested_dict(v)
		else:
			yield v