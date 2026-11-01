
import joblib
import pandas as pd
import numpy as np

from pathlib import Path
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.metrics import precision_score, recall_score, f1_score

# -------------------------------------------------
# 1. LOAD TRAINING DATA AND MODEL
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

train_path = BASE_DIR / "data" / "processed" / "train.csv"
model_path = BASE_DIR / "ml_model" / "saved_models" / "best_donor_model_v2.joblib"

train = pd.read_csv(train_path)
saved_data = joblib.load(model_path)

X_train = train[saved_data["features"]]
y_train = train[saved_data["target"]]

model = saved_data["model"]

# -------------------------------------------------
# 2. GROUP IDENTICAL FEATURE COMBINATIONS
# -------------------------------------------------

groups = pd.MultiIndex.from_frame(X_train).factorize()[0]

cv = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

# -------------------------------------------------
# 3. GENERATE OUT-OF-FOLD PROBABILITIES
# -------------------------------------------------

oof_probabilities = cross_val_predict(
    model,
    X_train,
    y_train,
    cv=cv,
    groups=groups,
    method="predict_proba",
    n_jobs=-1
)[:, 1]

# -------------------------------------------------
# 4. COMPARE THRESHOLDS
# -------------------------------------------------

print("\nLIFEFLOW - TRAINING-ONLY THRESHOLD SELECTION")
print("Priority: HIGH RECALL")

print("\nThreshold | Precision | Recall | F1 Score")

results = []

for threshold in np.arange(0.10, 0.81, 0.05):

    predictions = (oof_probabilities >= threshold).astype(int)

    precision = precision_score(
        y_train, predictions, zero_division=0
    )

    recall = recall_score(
        y_train, predictions, zero_division=0
    )

    f1 = f1_score(
        y_train, predictions, zero_division=0
    )

    results.append({
        "threshold": round(float(threshold), 2),
        "precision": precision,
        "recall": recall,
        "f1": f1
    })

    print(
        f"{threshold:.2f}      | "
        f"{precision:.3f}     | "
        f"{recall:.3f} | "
        f"{f1:.3f}"
    )

# -------------------------------------------------
# 5. SELECT A HIGH-RECALL THRESHOLD
# -------------------------------------------------

# Choose the highest threshold that achieves at least
# 90% recall on out-of-fold training predictions.

minimum_recall = 0.90

eligible = [
    result for result in results
    if result["recall"] >= minimum_recall
]

if not eligible:
    print("\nNo threshold achieved the required recall.")
else:
    selected = max(
        eligible,
        key=lambda result: result["threshold"]
    )

    print("\nSELECTED TRAINING THRESHOLD")
    print("Threshold:", selected["threshold"])
    print("Precision:", round(selected["precision"], 4))
    print("Recall:", round(selected["recall"], 4))
    print("F1 Score:", round(selected["f1"], 4))

    threshold_path = (
        BASE_DIR / "ml_model" / "saved_models"
        / "donor_threshold_v2.joblib"
    )

    joblib.dump({
        "threshold": selected["threshold"],
        "minimum_recall_target": minimum_recall,
        "selection_method": "5-fold StratifiedGroupKFold OOF",
        "priority": "high_recall"
    }, threshold_path)

    print("\nThreshold saved successfully:")
    print(threshold_path)
