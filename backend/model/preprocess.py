import numpy as np
from scipy.signal import butter, filtfilt, iirnotch, resample

def bandpass(signal, fs, lowcut=0.5, highcut=40.0, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)

def notch_filter(signal, fs, freq=60.0, Q=30.0):
    nyq = 0.5 * fs
    w0 = freq / nyq
    b, a = iirnotch(w0, Q)
    return filtfilt(b, a, signal)

def standardize(signal):
    mean = np.mean(signal)
    std = np.std(signal) + 1e-8
    return (signal - mean) / std

def resample_to(signal, fs_in, fs_out=250):
    if fs_in == fs_out:
        return signal, fs_in
    n_out = int(len(signal) * fs_out / fs_in)
    return resample(signal, n_out), fs_out

