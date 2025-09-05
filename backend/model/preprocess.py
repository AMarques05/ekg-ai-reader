import numpy as np
from scipy.signal import butter, filtfilt, iirnotch, resample

#Ensures to keep only the frequencies between 0.5 to 40hz to prevent confustion from R-Peaks to RR-Interval
def bandpass(signal, fs, lowcut=0.5, highcut=40.0, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)

#Filter process to cut our powerline interface
def notch_filter(signal, fs, freq=60.0, Q=30.0):
    nyq = 0.5 * fs
    w0 = freq / nyq
    b, a = iirnotch(w0, Q)
    return filtfilt(b, a, signal)

#Standardizs our signal between 0 and 1 no matter the raw amplitude
def standardize(signal):
    mean = np.mean(signal)
    std = np.std(signal) + 1e-8
    return (signal - mean) / std

#Converts signal sampling rate to 250hz
def resample_to(signal, fs_in, fs_out=250):
    if fs_in == fs_out:
        return signal, fs_in
    n_out = int(len(signal) * fs_out / fs_in)
    return resample(signal, n_out), fs_out

#Splits signals up into "Windows" that overlap by 1s to increase accuracy and in-case abnormality occurs on "border"
def make_windows_fixed(signal, fs, win_sec=2.0, step_sec=1.0):
    win = int(win_sec * fs)     
    step = int(step_sec * fs)
    windows = []
    for start in range(0, len(signal) - win + 1, step):
        windows.append(signal[start:start+win])
    return np.array(windows)
