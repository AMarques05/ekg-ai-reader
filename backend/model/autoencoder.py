import tensorflow as tf
from tensorflow.keras import layers, models


def build_autoencoder(input_len):
    """
    Build a simple Conv1D autoencoder for EKG windows.
    
    input_len: number of samples in one window (e.g., 500 for 2s at 250Hz)
    """
    inp = layers.Input(shape=(input_len, 1))

    # Encoder
    x = layers.Conv1D(32, 7, activation='relu', padding='same')(inp)
    x = layers.MaxPooling1D(2)(x)
    x = layers.Conv1D(16, 7, activation='relu', padding='same')(x)
    x = layers.MaxPooling1D(2)(x)

    # Latent space
    x = layers.Conv1D(8, 7, activation='relu', padding='same')(x)

    # Decoder
    x = layers.UpSampling1D(2)(x)
    x = layers.Conv1D(16, 7, activation='relu', padding='same')(x)
    x = layers.UpSampling1D(2)(x)
    out = layers.Conv1D(1, 7, activation='linear', padding='same')(x)

    model = models.Model(inp, out)
    model.compile(optimizer='adam', loss='mse')
    return model
