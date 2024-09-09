import numpy as np
import os
import inspect
import sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def load_formatted_data(filename="formatted_data.npz"):
    """Loads the formatted data from a .npz file."""
    filepath = os.path.join(current_dir, filename)
    data = np.load(filepath)
    X = data['X']
    y = data['y']
    return X, y

def display_first_100(X, y):
    """Displays the first 100 rows of the formatted data."""
    for i in range(min(100, len(X))):
        print(f"Data Row {i + 1}")
        print("Board State:")
        print(X[i])
        print("Score:")
        print(y[i])
        print("-" * 50)

if __name__ == "__main__":
    X, y = load_formatted_data("formatted_data.npz")
    
    display_first_100(X, y)
