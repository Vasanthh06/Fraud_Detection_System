import pandas as pd
import random

data = []

countries = [
    "India",
    "USA",
    "China",
    "Russia",
    "Other"
]

for i in range(5000):

    amount = random.randint(
        100,
        300000
    )

    country = random.choice(
        countries
    )

    transaction_hour = random.randint(
        0,
        23
    )

    failed_attempts = random.randint(
        0,
        6
    )

    fraud = 0

    # Fraud Conditions

    if (
        amount > 200000
        and country in ["Russia", "China"]
    ):
        fraud = 1

    if failed_attempts >= 5:
        fraud = 1

    if (
        transaction_hour <= 4
        and amount > 100000
    ):
        fraud = 1

    data.append(
        [
            amount,
            country,
            transaction_hour,
            failed_attempts,
            fraud
        ]
    )

df = pd.DataFrame(
    data,
    columns=[
        "amount",
        "country",
        "transaction_hour",
        "failed_attempts",
        "is_fraud"
    ]
)

df.to_csv(
    "dataset/ecommerce_fraud.csv",
    index=False
)

print(
    "Dataset Generated Successfully!"
)