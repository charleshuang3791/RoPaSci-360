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

    PRUNE_FACTOR = 0.995

    largest_equil_score_index = (0, 0)

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

        if self.turns_completed == 0:
            piece_to_throw = self.pieces_names_list[random.randrange(3)]
            self.turns_completed += 1
            if self.our_side == "lower":
                return ("THROW", piece_to_throw, (-4, 2))
            else:
                return ("THROW", piece_to_throw, (4, -2))

        # commence states_tree building / equilibrium solution finding
        depth = 2 # only two works because of scaling and largest_equil_score_index being global
        
        our_moves, their_moves, copy_of_our_pieces, copy_of_their_pieces = give_all_moves(self, copy.deepcopy(self.our_pieces), copy.deepcopy(self.their_pieces))
        if len(our_moves) == 1:
            return our_moves[0]

        scores_tree = []
        nth_level_of_scores_tree = []
        matrix_rows_num = len(our_moves)
        matrix_cols_num = len(their_moves)
        possible_moves_matrix = np.empty((matrix_rows_num, matrix_cols_num))
        possible_moves_matrix[:] = np.nan
        nth_level_of_scores_tree.append(possible_moves_matrix)
        scores_tree.append(nth_level_of_scores_tree)
        
        # starting our board states states_tree
        creating_nth_level_of_states_tree = 0
        states_tree = []
        nth_level_of_states_tree = []
        node = [our_moves, their_moves, copy_of_our_pieces, copy_of_their_pieces]
        nth_level_of_states_tree.append(node)
        states_tree.append(nth_level_of_states_tree)

        # This will iterate to create the remainder of the trees to our desired depth.
        # We are at the level of states_tree branches.
        for x in range(depth - 1):
            creating_nth_level_of_states_tree += 1
            nth_level_of_states_tree = []
            level_above = states_tree[creating_nth_level_of_states_tree - 1]
            level_above_score_ver = scores_tree[creating_nth_level_of_states_tree - 1]

            nth_level_of_scores_tree = []

            for score_parent_index, parent in enumerate(level_above):
                temp_our_moves = parent[0]
                temp_their_moves = parent[1]
                temp_our_pieces = parent[2]
                temp_their_pieces = parent[3]

                evaluation_scores_for_pruning = {}

                for our_move in temp_our_moves:
                    evaluation_scores_for_pruning[our_move] = {}
                    for their_move in temp_their_moves:
                        temp_updated_pieces = give_updated_pieces(self, their_move, our_move, copy.deepcopy(temp_their_pieces), copy.deepcopy(temp_our_pieces))
                        temp_our_new_pieces = temp_updated_pieces[1]
                        temp_their_new_pieces = temp_updated_pieces[0]

                        evaluation_scores_for_pruning[our_move][their_move] = evaluation(self, temp_our_new_pieces, temp_their_new_pieces)
                        
                        # adding moves of pieces already on the board
                        temp_our_new_moves, temp_their_new_moves, temp_our_new_pieces, temp_their_new_pieces = give_all_moves(self, copy.deepcopy(temp_our_new_pieces), copy.deepcopy(temp_their_new_pieces))

                        node = [temp_our_new_moves, temp_their_new_moves, temp_our_new_pieces, temp_their_new_pieces]
                        
                        matrix_rows_num = len(temp_our_new_moves)
                        matrix_cols_num = len(temp_their_new_moves)
                        possible_moves_matrix = np.empty((matrix_rows_num, matrix_cols_num))
                        possible_moves_matrix[:] = np.nan
                        nth_level_of_scores_tree.append(possible_moves_matrix)
                        
                        nth_level_of_states_tree.append(node)

                evaluation_scores_for_pruning_list = sorted(list(give_values_of_nested_dict(evaluation_scores_for_pruning)))
                prune_num = math.floor(self.PRUNE_FACTOR * len(evaluation_scores_for_pruning_list))
                del evaluation_scores_for_pruning_list[:prune_num]

                critical_value = evaluation_scores_for_pruning_list[0]
                largest_eval_score = evaluation_scores_for_pruning_list[-1]

                largest_equil_score_index_found = False
                for our_index, our_move in enumerate(temp_our_moves):
                    for their_index, their_move in enumerate(temp_their_moves):
                        if evaluation_scores_for_pruning[our_move][their_move] == largest_eval_score:
                            self.largest_equil_score_index = (our_index, their_index)
                            largest_equil_score_index_found = True

                        if largest_equil_score_index_found:
                            break
                    if largest_equil_score_index_found:
                        break

                # WARNING: THIS LIST IS JUST USED TO FIND A CRITICAL VALUE OF SCORES
                # THE LIST DOES NOT NECESSARILY REPRESENT THE NODES THAT WILL ACTUALLY BE DISCARDED
                # NODES WITH SCORES LOWER THAN THE CRITICAL VALUE WILL BE DISCARDED BELOW:

                nth_level_index = 0
                final_nth_level_of_states_tree = []
                final_nth_level_of_scores_tree = []
                for our_index, our_move in enumerate(temp_our_moves):
                    for their_index, their_move in enumerate(temp_their_moves):
                        if evaluation_scores_for_pruning[our_move][their_move] < critical_value:
                            level_above_score_ver[score_parent_index][our_index][their_index] = evaluation_scores_for_pruning[our_move][their_move] / largest_eval_score # as opposed to 0
                        else:
                            final_nth_level_of_states_tree.append(nth_level_of_states_tree[nth_level_index])
                            final_nth_level_of_scores_tree.append(nth_level_of_scores_tree[nth_level_index])
                        nth_level_index += 1
            states_tree.append(final_nth_level_of_states_tree)
            scores_tree.append(final_nth_level_of_scores_tree)

        # We are at states_tree leaf nodes level.
        states_tree = create_leaf_level_for_states_tree(self, states_tree)

        # Apply evaluation function at the leaf nodes
        for possible_moves_matrix in scores_tree[-1]:
            matrix_dimensions = np.shape(possible_moves_matrix)
            children_num = matrix_dimensions[0] * matrix_dimensions[1]
            children_nodes_from_states_tree = states_tree[-1][:children_num]
            del states_tree[-1][:children_num] # NOTE: this deletes the leaf nodes of the states tree
            possible_moves_matrix = fill_matrix_in1(self, possible_moves_matrix, children_nodes_from_states_tree)

        # Continue Back Propagation
        level_being_filled_in = -2
        while(1):
            for possible_moves_matrix in scores_tree[level_being_filled_in]:
                matrix_dimensions = np.shape(possible_moves_matrix)
                children_num = matrix_dimensions[0] * matrix_dimensions[1]
                children_nodes_from_scores_tree = scores_tree[level_being_filled_in + 1][:children_num]
                del scores_tree[level_being_filled_in + 1][:children_num] # NOTE: this deletes the nodes of the states tree
                possible_moves_matrix = fill_matrix_in2(self, possible_moves_matrix, children_nodes_from_scores_tree)

            if len(scores_tree[level_being_filled_in]) == 1:
                break

            level_being_filled_in -= 1

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