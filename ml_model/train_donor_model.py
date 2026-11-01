
from pathlib import Path

import joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import StratifiedGroupKFold, cross_validate
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

TRAIN_PATH = BASE_DIR / "data" / "processed" / "train.csv"
TEST_PATH = BASE_DIR / "data" / "processed" / "test.csv"

MODEL_DIR = BASE_DIR / "ml_model" / "saved_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "best_donor_model_v2.joblib"

TARGET = "whether he/she donated blood in March 2007"

FEATURES = [
    "Recency (months)",
    "Frequency (times)",
    "Time (months)"
]


# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

train_data = pd.read_csv(TRAIN_PATH)
test_data = pd.read_csv(TEST_PATH)

X_train = train_data[FEATURES].copy()
y_train = train_data[TARGET].copy()

X_test = test_data[FEATURES].copy()
y_test = test_data[TARGET].copy()

print("\nLIFEFLOW - IMPROVED MODEL TRAINING")
print("=" * 60)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))


# --------------------------------------------------
# 3. CREATE GROUPS FOR CROSS-VALIDATION
# --------------------------------------------------

groups = pd.MultiIndex.from_frame(X_train).factorize()[0]

splitter = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


# --------------------------------------------------
# 4. DEFINE MODELS
# --------------------------------------------------

models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42
        ))
    ]),

    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42
    )
}


# --------------------------------------------------
# 5. CROSS-VALIDATION
# --------------------------------------------------

results = []
cv_models = {}

scoring = {
    "accuracy": "accuracy",
    "precision": "precision",
    "recall": "recall",
    "f1": "f1"
}

print("\nCROSS-VALIDATION RESULTS")
print("=" * 60)

for name, model in models.items():

    print(f"\nEvaluating: {name}")

    scores = cross_validate(
        model,
        X_train,
        y_train,
        groups=groups,
        cv=splitter,
        scoring=scoring,
        return_train_score=False,
        n_jobs=-1,
        error_score="raise"
    )

    mean_f1 = scores["test_f1"].mean()

    results.append({
        "Model": name,
        "Accuracy": scores["test_accuracy"].mean(),
        "Precision": scores["test_precision"].mean(),
        "Recall": scores["test_recall"].mean(),
        "F1 Score": mean_f1
    })

    cv_models[name] = model

    print(f"Mean Accuracy : {scores['test_accuracy'].mean():.4f}")
    print(f"Mean Precision: {scores['test_precision'].mean():.4f}")
    print(f"Mean Recall   : {scores['test_recall'].mean():.4f}")
    print(f"Mean F1 Score : {mean_f1:.4f}")


# --------------------------------------------------
# 6. SELECT BEST MODEL USING CV F1
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\nMODEL COMPARISON")
print("=" * 60)
print(results_df.to_string(index=False))

best_model_name = results_df.loc[
    results_df["F1 Score"].idxmax(),
    "Model"
]

best_model = cv_models[best_model_name]

print("\nSelected model:", best_model_name)


# --------------------------------------------------
# 7. TRAIN SELECTED MODEL ON FULL TRAINING DATA
# --------------------------------------------------

best_model.fit(X_train, y_train)


# --------------------------------------------------
# 8. FINAL TEST EVALUATION
# --------------------------------------------------

predictions = best_model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)
precision = precision_score(
    y_test, predictions, zero_division=0
)
recall = recall_score(
    y_test, predictions, zero_division=0
)
f1 = f1_score(
    y_test, predictions, zero_division=0
)

print("\nFINAL INDEPENDENT TEST RESULTS")
print("=" * 60)

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))


# --------------------------------------------------
# 9. SAVE AS A NEW MODEL FILE
# --------------------------------------------------

joblib.dump({
    "model": best_model,
    "model_name": best_model_name,
    "features": FEATURES,
    "target": TARGET,
    "cv_results": results,
    "test_metrics": {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }
}, MODEL_PATH)


print("\nNEW MODEL SAVED SUCCESSFULLY!")
print("Model:", best_model_name)
print("Location:", MODEL_PATH)
print("\nOriginal model remains unchanged.")
