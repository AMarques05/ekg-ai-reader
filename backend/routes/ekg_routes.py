from flask import Blueprint, request, jsonify
import os
import io
import json
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

# Add model directory to path for importing preprocess
import sys
model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
sys.path.insert(0, model_dir)
import preprocess

bp = Blueprint("ekg", __name__)

# Lazy-load the trained Keras autoencoder
_model = None
_model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model", "saved", "autoencoder.h5")
_calibration = None
_calibration_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model", "saved", "calibration.json")

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(_model_path):
            raise FileNotFoundError(f"Model file not found at: {_model_path}")
        # Load without compiling to avoid deserializing legacy metrics/loss objects
        _model = load_model(_model_path, compile=False)
    return _model


def load_calibration():
    """Loads hybrid decision thresholds if available."""
    global _calibration
    if _calibration is not None:
        return _calibration
    if os.path.exists(_calibration_path):
        try:
            with open(_calibration_path, "r", encoding="utf-8") as f:
                _calibration = json.load(f)
        except Exception:
            _calibration = None
    return _calibration


def feature_amplitude(sig_filtered: np.ndarray) -> dict:
    return {
        "std": float(np.std(sig_filtered)),
        "ptp": float(np.ptp(sig_filtered)),
        "mad": float(np.median(np.abs(sig_filtered - np.median(sig_filtered))))
    }


def feature_autocorr_peak(sig: np.ndarray, fs: int = 250, min_bpm: int = 50, max_bpm: int = 150) -> float:
    x = (sig - np.mean(sig)) / (np.std(sig) + 1e-8)
    n = len(x)
    if n < int(fs * 0.6):
        return 0.0
    ac = np.correlate(x, x, mode='full')[n-1:]
    ac /= (ac[0] + 1e-8)
    min_lag = int(fs * 60.0 / max_bpm)
    max_lag = int(fs * 60.0 / min_bpm)
    if max_lag <= min_lag + 1 or max_lag >= len(ac):
        return 0.0
    return float(np.max(ac[min_lag:max_lag]))


def predict_from_values(values: np.ndarray, threshold: float = 0.00012, use_hybrid: bool = False) -> dict:
    """Core prediction logic used by the HTTP route and by local evaluators."""
    fs_in = 250
    sig, fs = preprocess.resample_to(values, fs_in, 250)
    sig = preprocess.notch_filter(sig, fs)
    sig = preprocess.bandpass(sig, fs)
    sig_filtered = sig.copy()
    sig = preprocess.standardize(sig)
    windows = preprocess.make_windows_fixed(sig, fs, win_sec=2.0, step_sec=1.0)

    if windows.size == 0:
        raise ValueError("Signal too short to form any windows")

    X = windows[..., None]
    model = get_model()
    recon = model.predict(X, verbose=0)
    mse = np.mean((X - recon) ** 2, axis=(1, 2))
    avg_mse = float(np.mean(mse))
    result = "normal" if avg_mse <= threshold else "abnormal"

    flags = []
    if use_hybrid:
        calib = load_calibration()
        if calib is not None:
            fa = feature_amplitude(sig_filtered)
            acp = feature_autocorr_peak(sig_filtered, fs=fs)
            amp_out = (fa["std"] < calib.get("amp_std_lo", 0.0) or fa["std"] > calib.get("amp_std_hi", float("inf")) or
                       fa["ptp"] < calib.get("amp_ptp_lo", 0.0) or fa["ptp"] > calib.get("amp_ptp_hi", float("inf")))
            irreg = acp < calib.get("ac_peak_lo", 0.0)
            if amp_out:
                result = "abnormal"
                flags.append("AMP")
            if irreg:
                result = "abnormal"
                flags.append("AC")

    return {
        "result": result,
        "reconstruction_error": avg_mse,
        "threshold": threshold,
        "windows": int(len(mse)),
        "samples_processed": int(len(values)),
        "flags": flags,
        "hybrid": bool(use_hybrid),
    }

def parse_file_data(file):
    """
    Parse uploaded file and extract EKG values.
    Supports multiple formats: CSV, JSON, Excel, and plain text.
    
    Returns:
        numpy.ndarray: Array of EKG values
        str: Error message if parsing fails
    """
    filename = file.filename.lower()
    file_content = file.read()
    file.seek(0)  # Reset file pointer
    
    try:
        # CSV format (original implementation)
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
            if "value" in df.columns:
                return df["value"].to_numpy(dtype=float), None
            elif "lead_i" in df.columns:
                return df["lead_i"].to_numpy(dtype=float), None
            elif "lead_ii" in df.columns:
                return df["lead_ii"].to_numpy(dtype=float), None
            else:
                # Try to find any numeric column
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    return df[numeric_cols[0]].to_numpy(dtype=float), None
                else:
                    return None, "CSV must contain at least one numeric column (preferably 'value', 'lead_i', or 'lead_ii')"
        
        # JSON format
        elif filename.endswith('.json'):
            data = json.loads(file_content)
            
            # Handle different JSON structures
            if isinstance(data, dict):
                # Look for common EKG field names
                for key in ['values', 'data', 'ekg', 'signal', 'lead_i', 'lead_ii']:
                    if key in data:
                        values = np.array(data[key], dtype=float)
                        return values, None
                
                # If no common keys, try first numeric array found
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        try:
                            values = np.array(value, dtype=float)
                            return values, None
                        except:
                            continue
                            
                return None, "JSON must contain a numeric array with key 'values', 'data', 'ekg', 'signal', 'lead_i', or 'lead_ii'"
            
            elif isinstance(data, list):
                # Direct array of values
                values = np.array(data, dtype=float)
                return values, None
            else:
                return None, "JSON must contain either an object with numeric arrays or a direct numeric array"
        
        # Excel format
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
            if "value" in df.columns:
                return df["value"].to_numpy(dtype=float), None
            elif "lead_i" in df.columns:
                return df["lead_i"].to_numpy(dtype=float), None
            elif "lead_ii" in df.columns:
                return df["lead_ii"].to_numpy(dtype=float), None
            else:
                # Try first numeric column
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    return df[numeric_cols[0]].to_numpy(dtype=float), None
                else:
                    return None, "Excel file must contain at least one numeric column"
        
        # Plain text format (space, comma, or newline separated)
        elif filename.endswith('.txt'):
            text_content = file_content.decode('utf-8')
            
            # Try different separators
            for separator in ['\n', ',', ' ', '\t']:
                try:
                    values_str = text_content.strip().split(separator)
                    values = np.array([float(v.strip()) for v in values_str if v.strip()], dtype=float)
                    if len(values) > 100:  # Reasonable minimum for EKG data
                        return values, None
                except:
                    continue
            
            return None, "Text file must contain numeric values separated by newlines, commas, spaces, or tabs"
        
        else:
            return None, f"Unsupported file format. Supported formats: CSV, JSON, Excel (.xlsx/.xls), and Text (.txt)"
    
    except Exception as e:
        return None, f"Error parsing {filename}: {str(e)}"

@bp.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files.get("file")
        if not file or not file.filename:
            return jsonify({"error": "No file provided"}), 400

        try:
            threshold = float(request.args.get("threshold", 0.00012))  # Optimal threshold based on analysis
        except ValueError:
            return jsonify({"error": "Invalid threshold value"}), 400

        use_hybrid = str(request.args.get("use_hybrid", "false")).lower() in ("1", "true", "yes")

        # Parse file data using new multi-format parser
        values, error = parse_file_data(file)
        if error:
            return jsonify({"error": error}), 400

        if len(values) < 500:  # Need at least 2 seconds at 250 Hz
            return jsonify({"error": "Signal too short - need at least 500 samples (2 seconds at 250 Hz)"}), 400

        # Use shared prediction logic (optionally hybrid)
        out = predict_from_values(values, threshold=threshold, use_hybrid=use_hybrid)

        return jsonify({
            **out,
            "file_format": file.filename.split('.')[-1].upper(),
        })
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400
