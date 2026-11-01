
import joblib
import pandas as pd

from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "ml_model" / "saved_models" / "best_donor_model_v2.joblib"
THRESHOLD_PATH = BASE_DIR / "ml_model" / "saved_models" / "donor_threshold_v2.joblib"
TEST_PATH = BASE_DIR / "data" / "processed" / "test.csv"

# Load saved model and selected threshold
model_data = joblib.load(MODEL_PATH)
threshold_data = joblib.load(THRESHOLD_PATH)

model = model_data["model"]
features = model_data["features"]
target = model_data["target"]
threshold = threshold_data["threshold"]

# Load test data
test = pd.read_csv(TEST_PATH)

X_test = test[features]
y_test = test[target]

# Predict probabilities and apply selected threshold
probabilities = model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= threshold).astype(int)

# Evaluation
print("\nLIFEFLOW - FINAL TEST EVALUATION")
print("Selected threshold:", threshold)

print("\nAccuracy:", round(accuracy_score(y_test, predictions), 4))
print("Precision:", round(precision_score(y_test, predictions, zero_division=0), 4))
print("Recall:", round(recall_score(y_test, predictions, zero_division=0), 4))
print("F1 Score:", round(f1_score(y_test, predictions, zero_division=0), 4))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))
