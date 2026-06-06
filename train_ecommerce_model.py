import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

print("Loading Dataset...")

df = pd.read_csv(
    "dataset/ecommerce_fraud.csv"
)

# Encode Country

encoder = LabelEncoder()

df["country"] = encoder.fit_transform(
    df["country"]
)

X = df.drop(
    "is_fraud",
    axis=1
)

y = df["is_fraud"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("Training Model...")

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(
    X_train,
    y_train
)

predictions = model.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    predictions
)

print(
    f"Accuracy: {accuracy*100:.2f}%"
)

joblib.dump(
    model,
    "models/ecommerce_fraud_model.pkl"
)

joblib.dump(
    encoder,
    "models/ecommerce_encoder.pkl"
)

print("Model Saved Successfully!")