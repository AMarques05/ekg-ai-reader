import pandas as pd
import numpy as np
from backend.model import preprocess
from sklearn.model_selection import train_test_split

def load_csv(path):
    df = pd.read_csv(path)
    # Assume columns: time, value
    values = df['value'].to_numpy(dtype=float)
    fs = 250
    return values, fs

def preprocess_signal(values, fs):
    # 1. Resample to 250 Hz
    sig, fs = preprocess.resample_to(values, fs, 250)

    # 2. Filter out noise
    sig = preprocess.notch_filter(sig, fs)
    sig = preprocess.bandpass(sig, fs)

    # 3. Standardize
    sig = preprocess.standardize(sig)

    return sig, fs

def make_windows(sig, fs, win_sec=2.0, step_sec=1.0):
    windows = preprocess.make_windows_fixed(sig, fs, win_sec, step_sec)
    return windows[..., None]

def save_datasets(csv_path, out_train="data/processed/X_train.npy", out_val="data/processed/X_val.npy"):
    values, fs = load_csv(csv_path)
    sig, fs = preprocess_signal(values, fs)
    X = make_windows(sig, fs)

    # Split 80% train, 20% validation
    X_train, X_val = train_test_split(X, test_size=0.2, random_state=42)

    np.save(out_train, X_train)
    np.save(out_val, X_val)
    print(f"Saved {X_train.shape[0]} train windows and {X_val.shape[0]} val windows.")
