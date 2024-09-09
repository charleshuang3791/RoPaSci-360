import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# Enable mixed precision if GPU supports it
tf.keras.mixed_precision.set_global_policy('mixed_float16')

import os
import inspect
import sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def load_formatted_data(filename):
    filepath = os.path.join(current_dir, filename)
    data = np.load(filepath)
    X = data['X']
    y = data['y']
    return X, y

def build_model(input_shape):
    """Builds a neural network model (more efficient than previous version)."""
    model = Sequential([
        Flatten(input_shape=input_shape),
        Dense(64, activation='relu'),  # Reduced number of neurons
        Dense(32, activation='relu'),  # Further reduced neurons
        Dense(1, activation='linear', dtype='float32')  # Keep output precision
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
    return model

def train_model(model, X, y, epochs=10, batch_size=64):
    """Trains the model on the provided data with early stopping."""
    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2, callbacks=[early_stopping])
    return model

if __name__ == "__main__":
    X, y = load_formatted_data("formatted_data.npz")
    
    model = build_model(X.shape[1:])
    
    model = train_model(model, X, y, epochs=20, batch_size=64)
    
    filepath = os.path.join(current_dir, "trained_model.h5")
    model.save(filepath)
    print("Model trained and saved as 'trained_model.h5'.")