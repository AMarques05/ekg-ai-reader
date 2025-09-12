"""
Download and process MIT-BIH Arrhythmia Database for Normal Sinus Rhythm training data.
This script downloads MIT-BIH records and filters for normal sinus rhythm segments.
"""

import os
import requests
import wfdb
import numpy as np
import pandas as pd
from pathlib import Path

# MIT-BIH database info
# Records with predominantly normal sinus rhythm (avoiding known arrhythmia cases)
NORMAL_RECORDS = [
    '100', '101', '103', '105', '111', '113', '115', '117', '121', '123'
]

# PhysioNet base URL for MIT-BIH
PHYSIONET_URL = "https://physionet.org/files/mitdb/1.0.0/"

def download_mitbih_record(record_id, data_dir):
    """Download a single MIT-BIH record (.dat, .hea, .atr files)"""
    print(f"Downloading record {record_id}...")
    
    for ext in ['.dat', '.hea', '.atr']:
        url = f"{PHYSIONET_URL}{record_id}{ext}"
        filepath = data_dir / f"{record_id}{ext}"
        
        if filepath.exists():
            print(f"  {record_id}{ext} already exists, skipping")
            continue
            
        response = requests.get(url)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"  Downloaded {record_id}{ext}")
        else:
            print(f"  Failed to download {record_id}{ext}")
            return False
    return True

def extract_normal_segments(record_id, data_dir):
    """Extract normal sinus rhythm segments from a MIT-BIH record"""
    record_path = str(data_dir / record_id)
    
    try:
        # Read the record
        record = wfdb.rdrecord(record_path)
        annotation = wfdb.rdann(record_path, 'atr')
        
        # Get ECG signal (use Lead II - channel 1 if available, else channel 0)
        if record.n_sig > 1:
            signal = record.p_signal[:, 1]  # Lead II
        else:
            signal = record.p_signal[:, 0]  # Lead I
            
        fs = record.fs  # Sampling frequency (360 Hz for MIT-BIH)
        
        # Find normal beats (annotation symbol 'N')
        normal_indices = []
        for i, symbol in enumerate(annotation.symbol):
            if symbol in ['N', '.']:  # Normal beat or not annotated (assumed normal)
                normal_indices.append(annotation.sample[i])
        
        # Extract segments around normal beats (±2 seconds)
        segment_length = int(4 * fs)  # 4 seconds total
        normal_segments = []
        
        for beat_idx in normal_indices:
            start = max(0, beat_idx - segment_length // 2)
            end = min(len(signal), beat_idx + segment_length // 2)
            
            if end - start >= segment_length * 0.8:  # At least 80% of desired length
                segment = signal[start:end]
                normal_segments.append(segment)
        
        return normal_segments, fs
        
    except Exception as e:
        print(f"Error processing record {record_id}: {e}")
        return [], 360

def create_training_csv(all_segments, fs, output_path):
    """Combine all normal segments into a single CSV for training"""
    print("Creating training CSV...")
    
    # Concatenate all segments with small gaps
    gap_length = int(0.1 * fs)  # 0.1 second gap between segments
    gap = np.zeros(gap_length)
    
    combined_signal = []
    for i, segment in enumerate(all_segments):
        combined_signal.extend(segment)
        if i < len(all_segments) - 1:  # Add gap except after last segment
            combined_signal.extend(gap)
    
    # Create time array
    time_ms = np.arange(len(combined_signal)) * (1000 / fs)
    
    # Create DataFrame
    df = pd.DataFrame({
        'time': time_ms,
        'value': combined_signal
    })
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Saved {len(combined_signal)} samples to {output_path}")
    print(f"Duration: {len(combined_signal) / fs:.1f} seconds")
    return len(combined_signal)

def main():
    """Main function to download and process MIT-BIH data"""
    # Setup directories
    data_dir = Path(__file__).parent / "raw"
    processed_dir = Path(__file__).parent / "processed"
    data_dir.mkdir(exist_ok=True)
    processed_dir.mkdir(exist_ok=True)
    
    print("Downloading MIT-BIH Normal Sinus Rhythm data...")
    print(f"Records to download: {NORMAL_RECORDS}")
    
    # Check if wfdb is installed
    try:
        import wfdb
    except ImportError:
        print("Error: wfdb package not found. Install with: pip install wfdb")
        return
    
    all_normal_segments = []
    sampling_freq = 360  # MIT-BIH default
    
    # Download and process each record
    for record_id in NORMAL_RECORDS:
        # Download record files
        if download_mitbih_record(record_id, data_dir):
            # Extract normal segments
            segments, fs = extract_normal_segments(record_id, data_dir)
            all_normal_segments.extend(segments)
            sampling_freq = fs
            print(f"  Extracted {len(segments)} normal segments from record {record_id}")
        else:
            print(f"  Skipping record {record_id} due to download failure")
    
    if all_normal_segments:
        # Create training CSV
        output_path = processed_dir / "mitbih_normal.csv"
        total_samples = create_training_csv(all_normal_segments, sampling_freq, output_path)
        
        print(f"\nSuccess! Created training data with {len(all_normal_segments)} segments")
        print(f"Total samples: {total_samples}")
        print(f"Sampling rate: {sampling_freq} Hz")
        print(f"Output: {output_path}")
    else:
        print("No normal segments extracted. Check your internet connection and try again.")

if __name__ == "__main__":
    main()