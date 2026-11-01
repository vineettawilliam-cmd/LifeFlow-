
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedGroupKFold

# 1. File paths
DATA_DIR = Path("data")
OUTPUT_DIR = DATA_DIR / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "transfusion.data"

# 2. Load original dataset
df = pd.read_csv(INPUT_FILE)

# 3. Separate features and target
target_column = "whether he/she donated blood in March 2007"

# Monetary is removed because it equals Frequency * 250
feature_columns = [
    "Recency (months)",
    "Frequency (times)",
    "Time (months)"
]

X = df[feature_columns].copy()
y = df[target_column].copy()

# 4. Create groups using identical feature combinations
groups = pd.MultiIndex.from_frame(X).factorize()[0]

# 5. Split without placing identical feature groups
# in both training and testing data
splitter = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

train_indices, test_indices = next(
    splitter.split(X, y, groups)
)

X_train = X.iloc[train_indices].copy()
X_test = X.iloc[test_indices].copy()

y_train = y.iloc[train_indices].copy()
y_test = y.iloc[test_indices].copy()

# 6. Verify no group leakage
train_groups = set(groups[train_indices])
test_groups = set(groups[test_indices])

assert train_groups.isdisjoint(test_groups), (
    "Data leakage detected!"
)

# 7. Save processed datasets
train_df = X_train.copy()
train_df[target_column] = y_train

test_df = X_test.copy()
test_df[target_column] = y_test

train_df.to_csv(OUTPUT_DIR / "train.csv", index=False)
test_df.to_csv(OUTPUT_DIR / "test.csv", index=False)

# 8. Display report
print("\nDATA PREPROCESSING COMPLETED")
print("-" * 45)

print("Original records:", len(df))
print("Training records:", len(train_df))
print("Testing records:", len(test_df))

print("\nTraining target distribution:")
print(y_train.value_counts())

print("\nTesting target distribution:")
print(y_test.value_counts())

print("\nFeatures used:", feature_columns)
print("Removed feature: Monetary (redundant)")

print("\nGroups shared between train and test:", 
      len(train_groups.intersection(test_groups)))

print("\nSaved files:")
print(OUTPUT_DIR / "train.csv")
print(OUTPUT_DIR / "test.csv")
