import numpy as np
import json
import os
import inspect
import sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def initialize_empty_board():
    """Initializes an empty 9x9 board with (0, 0, 0, 0, 0, 0) tuples."""
    return np.zeros((9, 9, 6), dtype=int)

def coordinate_to_index(coord):
    """Converts board coordinates (r, q) to matrix indices (i, j)."""
    r, q = coord
    i = r + 4
    j = q + 4
    return i, j

def place_piece_on_board(board, piece_type, coord, is_opponent=False):
    """Places a piece on the board based on its type and coordinate."""
    i, j = coordinate_to_index(coord)
    
    if not is_opponent:
        if piece_type == 'r':
            board[i, j] = [0, 1, 0, 0, 0, 0]  # Player's Rock
        elif piece_type == 'p':
            board[i, j] = [0, 0, 1, 0, 0, 0]  # Player's Paper
        elif piece_type == 's':
            board[i, j] = [1, 0, 0, 0, 0, 0]  # Player's Scissors
    else:
        if piece_type == 'r':
            board[i, j] = [0, 0, 0, 0, 1, 0]  # Opponent's Rock
        elif piece_type == 'p':
            board[i, j] = [0, 0, 0, 0, 0, 1]  # Opponent's Paper
        elif piece_type == 's':
            board[i, j] = [0, 0, 0, 1, 0, 0]  # Opponent's Scissors

def format_board_state(our_pieces, their_pieces):
    """Formats the board state into a 9x9 matrix with tuples."""
    board = initialize_empty_board()
    
    for piece_type in our_pieces:
        if piece_type != 'throws_left':  # Ignore the throws_left key
            for coord in our_pieces[piece_type]:
                place_piece_on_board(board, piece_type, coord)
    
    for piece_type in their_pieces:
        if piece_type != 'throws_left':
            for coord in their_pieces[piece_type]:
                place_piece_on_board(board, piece_type, coord, is_opponent=True)
    
    return board

def format_data_for_nn(data):
    """
    Converts a list of board states and scores into a format suitable for training a neural network.
    
    Arguments:
    - data: List of tuples [(board_state, score), ...]
    
    Returns:
    - X: List of formatted board states (as 9x9x6 numpy arrays)
    - y: List of corresponding scores
    """
    X = []
    y = []
    
    for board_state, score in data:
        our_pieces, their_pieces = board_state
        board_matrix = format_board_state(our_pieces, their_pieces)
        X.append(board_matrix)
        y.append(score)
    
    return np.array(X), np.array(y)

def save_formatted_data(X, y, filename="formatted_data.npz"):
    """
    Saves the formatted data to a .npz file.
    
    Arguments:
    - X: Array of formatted board states.
    - y: Array of corresponding scores.
    - filename
    """
    
    filepath = os.path.join(current_dir, filename)
    np.savez_compressed(filepath, X=X, y=y)
    print(f"Data saved to {filename}")

def load_training_data(filename="training_data.json"):
    filepath = os.path.join(current_dir, filename)
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    # Load the training data from the JSON file
    data = load_training_data("training_data.json")
    
    # Format the data for neural network input
    X, y = format_data_for_nn(data)
    
    # Save the formatted data
    save_formatted_data(X, y, "formatted_data.npz")
