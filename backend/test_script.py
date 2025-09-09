import numpy as np

X_train = np.load("backend/data/processed/X_train.npy")
X_val   = np.load("backend/data/processed/X_val.npy")

print("Train shape:", X_train.shape)
print("Val shape:", X_val.shape)