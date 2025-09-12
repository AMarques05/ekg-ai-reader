"""
Generate test datasets for validating the MIT-BIH trained autoencoder.
Creates both normal and abnormal ECG samples for testing.
"""

import numpy as np
import pandas as pd
import os
from pathlib import Path

def create_normal_test_data():
    """Create synthetic normal ECG data"""
    # Simulate normal sinus rhythm: ~70 BPM, regular intervals
    fs = 250  # Hz
    duration = 10  # seconds
    t = np.linspace(0, duration, int(fs * duration))
    
    # Heart rate parameters
    heart_rate = 70  # BPM
    rr_interval = 60 / heart_rate  # seconds between beats
    
    signal = np.zeros_like(t)
    
    # Generate R-peaks at regular intervals
    beat_times = np.arange(0, duration, rr_interval)
    
    for beat_time in beat_times:
        if beat_time < duration:
            # Simple QRS complex model
            beat_idx = int(beat_time * fs)
            
            # P wave (small positive deflection)
            p_start = max(0, beat_idx - int(0.15 * fs))
            p_end = max(0, beat_idx - int(0.05 * fs))
            if p_end > p_start:
                signal[p_start:p_end] += 0.2 * np.sin(np.linspace(0, np.pi, p_end - p_start))
            
            # QRS complex (sharp spike)
            qrs_start = max(0, beat_idx - int(0.04 * fs))
            qrs_end = min(len(signal), beat_idx + int(0.04 * fs))
            if qrs_end > qrs_start:
                qrs_signal = np.concatenate([
                    -0.3 * np.ones(int(0.02 * fs)),  # Q wave
                    1.0 * np.ones(int(0.02 * fs)),   # R wave
                    -0.2 * np.ones(int(0.04 * fs))   # S wave
                ])
                qrs_len = min(len(qrs_signal), qrs_end - qrs_start)
                signal[qrs_start:qrs_start + qrs_len] += qrs_signal[:qrs_len]
            
            # T wave (broader positive deflection)
            t_start = min(len(signal), beat_idx + int(0.1 * fs))
            t_end = min(len(signal), beat_idx + int(0.3 * fs))
            if t_end > t_start:
                signal[t_start:t_end] += 0.3 * np.sin(np.linspace(0, np.pi, t_end - t_start))
    
    # Add small amount of noise
    noise = np.random.normal(0, 0.05, len(signal))
    signal += noise
    
    return t * 1000, signal  # Convert time to ms

def create_abnormal_test_data():
    """Create various abnormal ECG patterns"""
    abnormal_samples = {}
    
    # 1. Atrial Fibrillation (irregular rhythm)
    fs = 250
    duration = 10
    t = np.linspace(0, duration, int(fs * duration))
    
    signal_afib = np.zeros_like(t)
    # Irregular R-R intervals for AFib
    irregular_intervals = np.random.normal(0.8, 0.3, 15)  # Very irregular
    irregular_intervals = np.abs(irregular_intervals)  # Ensure positive
    
    beat_time = 0
    for interval in irregular_intervals:
        if beat_time < duration:
            beat_idx = int(beat_time * fs)
            # QRS without P waves (characteristic of AFib)
            qrs_start = max(0, beat_idx - int(0.04 * fs))
            qrs_end = min(len(signal_afib), beat_idx + int(0.04 * fs))
            if qrs_end > qrs_start:
                qrs_signal = np.concatenate([
                    -0.2 * np.ones(int(0.02 * fs)),
                    0.8 * np.ones(int(0.02 * fs)),
                    -0.1 * np.ones(int(0.04 * fs))
                ])
                qrs_len = min(len(qrs_signal), qrs_end - qrs_start)
                signal_afib[qrs_start:qrs_start + qrs_len] += qrs_signal[:qrs_len]
            
            beat_time += interval
    
    # Add fibrillatory waves
    fib_waves = 0.05 * np.sin(2 * np.pi * 4 * t) * np.random.random(len(t))
    signal_afib += fib_waves
    noise = np.random.normal(0, 0.08, len(signal_afib))
    signal_afib += noise
    
    abnormal_samples['atrial_fibrillation'] = (t * 1000, signal_afib)
    
    # 2. Bradycardia (slow heart rate)
    signal_brady = np.zeros_like(t)
    heart_rate = 45  # BPM (below normal)
    rr_interval = 60 / heart_rate
    
    beat_times = np.arange(0, duration, rr_interval)
    for beat_time in beat_times:
        if beat_time < duration:
            beat_idx = int(beat_time * fs)
            # Normal QRS but slow rate
            qrs_start = max(0, beat_idx - int(0.04 * fs))
            qrs_end = min(len(signal_brady), beat_idx + int(0.04 * fs))
            if qrs_end > qrs_start:
                qrs_signal = np.concatenate([
                    -0.3 * np.ones(int(0.02 * fs)),
                    1.0 * np.ones(int(0.02 * fs)),
                    -0.2 * np.ones(int(0.04 * fs))
                ])
                qrs_len = min(len(qrs_signal), qrs_end - qrs_start)
                signal_brady[qrs_start:qrs_start + qrs_len] += qrs_signal[:qrs_len]
    
    noise = np.random.normal(0, 0.05, len(signal_brady))
    signal_brady += noise
    abnormal_samples['bradycardia'] = (t * 1000, signal_brady)
    
    # 3. Tachycardia (fast heart rate)
    signal_tachy = np.zeros_like(t)
    heart_rate = 120  # BPM (above normal)
    rr_interval = 60 / heart_rate
    
    beat_times = np.arange(0, duration, rr_interval)
    for beat_time in beat_times:
        if beat_time < duration:
            beat_idx = int(beat_time * fs)
            qrs_start = max(0, beat_idx - int(0.03 * fs))  # Shorter QRS due to fast rate
            qrs_end = min(len(signal_tachy), beat_idx + int(0.03 * fs))
            if qrs_end > qrs_start:
                qrs_signal = np.concatenate([
                    -0.2 * np.ones(int(0.015 * fs)),
                    0.9 * np.ones(int(0.015 * fs)),
                    -0.1 * np.ones(int(0.03 * fs))
                ])
                qrs_len = min(len(qrs_signal), qrs_end - qrs_start)
                signal_tachy[qrs_start:qrs_start + qrs_len] += qrs_signal[:qrs_len]
    
    noise = np.random.normal(0, 0.06, len(signal_tachy))
    signal_tachy += noise
    abnormal_samples['tachycardia'] = (t * 1000, signal_tachy)
    
    # 4. Premature Ventricular Contractions (PVCs)
    signal_pvc = np.zeros_like(t)
    heart_rate = 75  # Normal base rate
    rr_interval = 60 / heart_rate
    
    beat_times = np.arange(0, duration, rr_interval)
    for i, beat_time in enumerate(beat_times):
        if beat_time < duration:
            beat_idx = int(beat_time * fs)
            
            # Every 4th beat is a PVC
            if i % 4 == 3:
                # PVC: wider, bizarre QRS
                qrs_start = max(0, beat_idx - int(0.08 * fs))
                qrs_end = min(len(signal_pvc), beat_idx + int(0.08 * fs))
                if qrs_end > qrs_start:
                    # Bizarre, wide QRS pattern
                    qrs_signal = np.concatenate([
                        -0.5 * np.ones(int(0.04 * fs)),
                        1.2 * np.ones(int(0.04 * fs)),
                        -0.4 * np.ones(int(0.08 * fs))
                    ])
                    qrs_len = min(len(qrs_signal), qrs_end - qrs_start)
                    signal_pvc[qrs_start:qrs_start + qrs_len] += qrs_signal[:qrs_len]
            else:
                # Normal QRS
                qrs_start = max(0, beat_idx - int(0.04 * fs))
                qrs_end = min(len(signal_pvc), beat_idx + int(0.04 * fs))
                if qrs_end > qrs_start:
                    qrs_signal = np.concatenate([
                        -0.3 * np.ones(int(0.02 * fs)),
                        1.0 * np.ones(int(0.02 * fs)),
                        -0.2 * np.ones(int(0.04 * fs))
                    ])
                    qrs_len = min(len(qrs_signal), qrs_end - qrs_start)
                    signal_pvc[qrs_start:qrs_start + qrs_len] += qrs_signal[:qrs_len]
    
    noise = np.random.normal(0, 0.05, len(signal_pvc))
    signal_pvc += noise
    abnormal_samples['pvc'] = (t * 1000, signal_pvc)
    
    return abnormal_samples

def save_test_datasets():
    """Save test datasets as CSV files"""
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(exist_ok=True)
    
    print("Creating test datasets...")
    
    # Create normal test data
    time_ms, normal_signal = create_normal_test_data()
    normal_df = pd.DataFrame({
        'time': time_ms,
        'value': normal_signal
    })
    normal_path = test_dir / "normal_test.csv"
    normal_df.to_csv(normal_path, index=False)
    print(f"Created normal test data: {normal_path}")
    
    # Create abnormal test data
    abnormal_samples = create_abnormal_test_data()
    
    for condition, (time_ms, signal) in abnormal_samples.items():
        df = pd.DataFrame({
            'time': time_ms,
            'value': signal
        })
        file_path = test_dir / f"{condition}_test.csv"
        df.to_csv(file_path, index=False)
        print(f"Created {condition} test data: {file_path}")
    
    print(f"\nTest datasets created in: {test_dir}")
    print("\nTo test your model:")
    print("1. Start your Flask backend: python backend/app.py")
    print("2. Upload these CSV files via frontend or Postman")
    print("3. Compare reconstruction errors:")
    print("   - Normal data should have LOW error (< threshold)")
    print("   - Abnormal data should have HIGH error (> threshold)")
    print("4. Adjust threshold in your Flask route if needed")

if __name__ == "__main__":
    save_test_datasets()