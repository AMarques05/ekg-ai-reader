from flask import Blueprint, request, jsonify
import os
import io
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from model import preprocess

bp = Blueprint("ekg", __name__)

# Lazy-load the trained Keras autoencoder
_model = None
_model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "autoencoder.h5")

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(_model_path):
            raise FileNotFoundError(f"Model file not found at: {_model_path}")
        # Load without compiling to avoid deserializing legacy metrics/loss objects
        _model = load_model(_model_path, compile=False)
    return _model

@bp.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files.get("file")
        if not file or not file.filename:
            return jsonify({"error": "No file provided"}), 400

        try:
            threshold = float(request.args.get("threshold", 0.02))
        except ValueError:
            return jsonify({"error": "Invalid threshold value"}), 400

        try:
            df = pd.read_csv(file)
        except Exception as e:
            return jsonify({"error": f"Invalid CSV: {e}"}), 400

        if "value" not in df.columns:
            return jsonify({"error": "CSV must contain a 'value' column"}), 400

        values = df["value"].to_numpy(dtype=float)
        fs_in = 250  

        sig, fs = preprocess.resample_to(values, fs_in, 250)
        sig = preprocess.notch_filter(sig, fs)
        sig = preprocess.bandpass(sig, fs)
        sig = preprocess.standardize(sig)
        windows = preprocess.make_windows_fixed(sig, fs, win_sec=2.0, step_sec=1.0)

        if windows.size == 0:
            return jsonify({"error": "Signal too short to form any windows"}), 400

        X = windows[..., None] 

        # Load model and run inference
        model = get_model()
        recon = model.predict(X, verbose=0)

        # Compute reconstruction error (MSE) per window and average
        mse = np.mean((X - recon) ** 2, axis=(1, 2))
        avg_mse = float(np.mean(mse))
        result = "normal" if avg_mse <= threshold else "abnormal"

        return jsonify({
            "result": result,
            "reconstruction_error": avg_mse,
            "threshold": threshold,
            "windows": int(len(mse))
        })
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400
