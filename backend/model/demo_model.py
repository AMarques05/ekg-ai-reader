import random
import joblib

class DemoModel:
    def __init__(self):
        self.labels = ["Normal", "AFib", "PVC", "Bradycardia","Other"]

    def predict(self, ekg_csv):
        return random.choice(self.labels)

# Save the dummy model
joblib.dump(DemoModel(), "model/saved/demo_model.pkl")
