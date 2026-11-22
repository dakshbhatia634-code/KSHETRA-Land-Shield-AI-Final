import pandas as pd
from pathlib import Path

base = Path("data/raw")

files = list(base.glob("*.csv")) + list(base.glob("*.parquet"))

if not files:
    print("No datasets found in data/raw")
else:
    for file in files:
        print("\n" + "=" * 70)
        print("FILE:", file.name)
        print("=" * 70)

        try:
            if file.suffix == ".parquet":
                df = pd.read_parquet(file)
            else:
                df = pd.read_csv(file)

            print("Shape:", df.shape)

            print("\nColumns:")
            print(df.columns.tolist())

            print("\nData Types:")
            print(df.dtypes)

            print("\nMissing Values:")
            print(df.isnull().sum())

            print("\nFirst 5 Rows:")
            print(df.head().to_string())

        except Exception as e:
            print("ERROR:", e)