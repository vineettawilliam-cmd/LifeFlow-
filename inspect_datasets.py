
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")

datasets = {
    "Transfusion Dataset": DATA_DIR / "transfusion.data",
    "Blood Donation Dataset": DATA_DIR / "blood_donation.csv",
}

for name, path in datasets.items():
    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    if not path.exists():
        print(f"Dataset not found: {path}")
        continue

    if path.suffix == ".data":
        df = pd.read_csv(path)
    else:
        df = pd.read_csv(path)

    print("\n1. Shape (Rows, Columns):")
    print(df.shape)

    print("\n2. Column Names:")
    print(df.columns.tolist())

    print("\n3. First 5 Records:")
    print(df.head())

    print("\n4. Data Types:")
    print(df.dtypes)

    print("\n5. Missing Values:")
    print(df.isnull().sum())

    print("\n6. Duplicate Records:")
    print(df.duplicated().sum())

    print("\n7. Statistical Summary:")
    print(df.describe(include="all"))

    print("\n8. Target/Class Distribution:")
    if "whether he/she donated blood in March 2007" in df.columns:
        print(df["whether he/she donated blood in March 2007"].value_counts())
    else:
        print("Target column not identified yet.")
