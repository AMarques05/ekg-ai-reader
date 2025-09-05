import numpy as np
import tensorflow as tf
from tensorflow.keras import callbacks
from model.autoencoder import build_autoencoder

def train_autoencoder(X_train, X_val, save_path="models/autoencoder.h5"):

    input_len = X_train.shape[1]  # number of samples per window

    # Build a fresh model
    model = build_autoencoder(input_len)

    # Early stopping: stop training if val_loss doesn't improve for 5 epochs
    es = callbacks.EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True
    )

    # Fit the model: input = X, target = X (reconstruction)
    history = model.fit(
        X_train, X_train,              # input and output are the same
        validation_data=(X_val, X_val),
        epochs=50,
        batch_size=128,
        callbacks=[es],
        verbose=2
    )

    # Save trained model
    model.save(save_path)
    print(f"Model saved to {save_path}")

    return history
