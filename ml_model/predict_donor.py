
from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "ml_model"
    / "saved_models"
    / "best_donor_model.joblib"
)

# Load the trained model
saved_data = joblib.load(MODEL_PATH)

model = saved_data["model"]
features = saved_data["features"]

print("Loaded model:", saved_data["model_name"])
print("Features:", features)

# Sample donor information
sample_donor = pd.DataFrame([{
    "Recency (months)": 2,
    "Frequency (times)": 5,
    "Time (months)": 30
}])

# Ensure correct feature order
sample_donor = sample_donor[features]

# Predict
prediction = model.predict(sample_donor)[0]
probability = model.predict_proba(sample_donor)[0][1]

print("\nDONOR PREDICTION")
print("------------------------------")
print("Predicted class:", prediction)
print(f"Estimated probability: {probability:.2%}")

if prediction == 1:
    print("Prediction: Likely to return to donate")
else:
    print("Prediction: Less likely to return to donate")
