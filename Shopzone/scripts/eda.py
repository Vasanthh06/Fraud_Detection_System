import pandas as pd

# Load Dataset
df = pd.read_csv("dataset/creditcard.csv")

print("=" * 50)
print("DATASET LOADED SUCCESSFULLY")
print("=" * 50)

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nFraud Distribution:")
print(df["Class"].value_counts())

print("\nFirst 5 Rows:")
print(df.head())