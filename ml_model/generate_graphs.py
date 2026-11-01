
from pathlib import Path
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "ml_model" / "saved_models"
OUTPUT_DIR = BASE_DIR / "ml_model" / "visualizations"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

original = pd.read_csv(DATA_DIR / "transfusion.data")
train = pd.read_csv(DATA_DIR / "processed" / "train.csv")
test = pd.read_csv(DATA_DIR / "processed" / "test.csv")

model_data = joblib.load(
    MODEL_DIR / "best_donor_model_v2.joblib"
)

threshold_data = joblib.load(
    MODEL_DIR / "donor_threshold_v2.joblib"
)

model = model_data["model"]
features = model_data["features"]
cv_results = pd.DataFrame(model_data["cv_results"])

threshold = float(threshold_data["threshold"])

target = "whether he/she donated blood in March 2007"

# --------------------------------------------------
# 3. GRAPH STYLE
# --------------------------------------------------

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (9, 5)
plt.rcParams["font.size"] = 11

def save_graph(filename):
    plt.tight_layout()
    plt.savefig(
        OUTPUT_DIR / filename,
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()
    print("Generated:", filename)

# --------------------------------------------------
# GRAPH 1: TARGET DISTRIBUTION
# --------------------------------------------------

counts = original[target].value_counts().sort_index()

plt.figure()
plt.bar(
    ["Did not donate", "Donated"],
    [counts.get(0, 0), counts.get(1, 0)]
)
plt.title("Blood Donation Target Distribution")
plt.xlabel("Donation Status")
plt.ylabel("Number of Records")

for i, value in enumerate(
    [counts.get(0, 0), counts.get(1, 0)]
):
    plt.text(i, value + 5, str(value), ha="center")

save_graph("01_target_distribution.png")

# --------------------------------------------------
# GRAPHS 2-4: FEATURE DISTRIBUTIONS
# --------------------------------------------------

feature_titles = {
    "Recency (months)": "Recency Distribution",
    "Frequency (times)": "Donation Frequency Distribution",
    "Time (months)": "Donation History Duration Distribution"
}

for feature, title in feature_titles.items():
    plt.figure()
    plt.hist(
        original[feature],
        bins=20,
        edgecolor="black"
    )
    plt.title(title)
    plt.xlabel(feature)
    plt.ylabel("Number of Records")
    save_graph(
        feature.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        + "_distribution.png"
    )

# --------------------------------------------------
# GRAPH 5: MODEL COMPARISON
# --------------------------------------------------

metrics = ["Accuracy", "Precision", "Recall", "F1 Score"]

cv_plot = cv_results.set_index("Model")[metrics]

ax = cv_plot.plot(
    kind="bar",
    figsize=(10, 6),
    ylim=(0, 1),
    rot=0
)

plt.title("Model Performance Comparison - Cross Validation")
plt.ylabel("Score")
plt.xlabel("ML Model")
plt.legend(loc="lower right")
save_graph("05_model_comparison.png")

# --------------------------------------------------
# GRAPH 6: CONFUSION MATRIX AT THRESHOLD 0.30
# --------------------------------------------------

X_test = test[features]
y_test = test[target]

probabilities = model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= threshold).astype(int)

cm = confusion_matrix(
    y_test,
    predictions,
    labels=[0, 1]
)

plt.figure(figsize=(7, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Not Donated", "Donated"],
    yticklabels=["Not Donated", "Donated"]
)

plt.title("Confusion Matrix - Threshold 0.30")
plt.xlabel("Predicted Label")
plt.ylabel("Actual Label")
save_graph("06_confusion_matrix_030.png")

# --------------------------------------------------
# GRAPH 7: TEST METRICS AT TWO THRESHOLDS
# --------------------------------------------------

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

thresholds = [0.50, 0.30]
threshold_results = []

for value in thresholds:
    pred = (probabilities >= value).astype(int)

    threshold_results.append({
        "Threshold": str(value),
        "Accuracy": accuracy_score(y_test, pred),
        "Precision": precision_score(
            y_test, pred, zero_division=0
        ),
        "Recall": recall_score(
            y_test, pred, zero_division=0
        ),
        "F1 Score": f1_score(
            y_test, pred, zero_division=0
        )
    })

threshold_df = pd.DataFrame(threshold_results)

ax = threshold_df.set_index("Threshold").plot(
    kind="bar",
    figsize=(9, 6),
    ylim=(0, 1),
    rot=0
)

plt.title("Test Performance at Different Thresholds")
plt.xlabel("Classification Threshold")
plt.ylabel("Score")
plt.legend(loc="lower right")
save_graph("07_threshold_comparison.png")

# --------------------------------------------------
# 8. SAVE METRICS FOR WEBSITE
# --------------------------------------------------

test_metrics = {
    "threshold": threshold,
    "accuracy": accuracy_score(y_test, predictions),
    "precision": precision_score(
        y_test, predictions, zero_division=0
    ),
    "recall": recall_score(
        y_test, predictions, zero_division=0
    ),
    "f1_score": f1_score(
        y_test, predictions, zero_division=0
    ),
    "confusion_matrix": cm.tolist()
}

joblib.dump(
    {
        "model_name": model_data["model_name"],
        "features": features,
        "cv_results": model_data["cv_results"],
        "test_metrics_at_deployed_threshold": test_metrics,
        "threshold_data": threshold_data
    },
    OUTPUT_DIR / "analytics_results.joblib"
)

print("\nAll graphs generated successfully!")
print("Output folder:", OUTPUT_DIR)
print("\nTest metrics at threshold", threshold)
print(test_metrics)
