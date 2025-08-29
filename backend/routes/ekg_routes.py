from flask import Blueprint, request, jsonify
import joblib
import os

bp = Blueprint("ekg", __name__)

try:
    model_path = "model/saved/demo_model.pkl"
    if os.path.exists(model_path) and os.path.getsize(model_path) > 0:
        model = joblib.load(model_path)
    else:
        model = None
        print(f"Warning: Model file {model_path} is empty or doesn't exist")
except Exception as e:
    model = None
    print(f"Error loading model: {e}")

@bp.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not available", "prediction": "Demo result - model not loaded"}), 200
    
    try:
        file = request.files["file"]
        if not file or not file.filename:
            return jsonify({"error": "No file provided"}), 400
            
        # Use the actual model to get a random prediction
        prediction = model.predict(file)
        return jsonify({"prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e), "prediction": "Error processing file"}), 400
