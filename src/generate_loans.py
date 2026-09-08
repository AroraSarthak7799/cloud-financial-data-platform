import random
from datetime import date, timedelta

import pandas as pd


random.seed(42)


LOAN_TERMS = [
    36,
    48,
    60,
    72,
    84,
]


LOAN_STATUSES = [
    "Active",
    "Paid Off",
    "Delinquent",
    "Defaulted",
]


def calculate_monthly_payment(
    loan_amount: float,
    annual_interest_rate: float,
    term_months: int,
) -> float:

    monthly_interest_rate = annual_interest_rate / 100 / 12

    monthly_payment = (
        loan_amount
        * monthly_interest_rate
        * (1 + monthly_interest_rate) ** term_months
        / (
            (1 + monthly_interest_rate) ** term_months
            - 1
        )
    )

    return round(monthly_payment, 2)


def generate_loans(
    number_of_loans: int,
    customer_file: str = "data/raw/customers.csv",
    vehicle_file: str = "data/raw/vehicles.csv",
) -> pd.DataFrame:

    customer_df = pd.read_csv(customer_file)

    vehicle_df = pd.read_csv(vehicle_file)

    customer_ids = customer_df["customer_id"].tolist()

    if number_of_loans > len(vehicle_df):
        raise ValueError(
            "Number of loans cannot exceed number of available vehicles."
        )

    selected_vehicles = vehicle_df.sample(
        n=number_of_loans,
        random_state=42,
    )

    loans = []

    today = date.today()

    for loan_number, (_, vehicle) in enumerate(
        selected_vehicles.iterrows(),
        start=1,
    ):
        customer_id = random.choice(customer_ids)

        purchase_price = float(vehicle["original_price"])

        down_payment_percentage = random.uniform(
            0.10,
            0.30,
        )

        down_payment = round(
            purchase_price * down_payment_percentage,
            2,
        )

        loan_amount = round(
            purchase_price - down_payment,
            2,
        )

        annual_interest_rate = round(
            random.uniform(4.50, 10.50),
            2,
        )

        term_months = random.choice(LOAN_TERMS)

        monthly_payment = calculate_monthly_payment(
            loan_amount,
            annual_interest_rate,
            term_months,
        )

        days_ago = random.randint(
            0,
            5 * 365,
        )

        loan_start_date = today - timedelta(
            days=days_ago
        )

        maturity_date = (
            pd.Timestamp(loan_start_date)
            + pd.DateOffset(months=term_months)
        ).date()

        if maturity_date < today:
            loan_status = "Paid Off"
        else:
            loan_status = random.choices(
                population=[
                    "Active",
                    "Delinquent",
                    "Defaulted",
                ],
                weights=[
                    85,
                    10,
                    5,
                ],
                k=1,
            )[0]

        loan = {
            "loan_id": f"LOAN{loan_number:06d}",
            "customer_id": customer_id,
            "vehicle_id": vehicle["vehicle_id"],
            "dealer_id": vehicle["dealer_id"],
            "loan_start_date": loan_start_date,
            "maturity_date": maturity_date,
            "original_price": purchase_price,
            "down_payment": down_payment,
            "loan_amount": loan_amount,
            "annual_interest_rate": annual_interest_rate,
            "term_months": term_months,
            "monthly_payment": monthly_payment,
            "loan_status": loan_status,
        }

        loans.append(loan)

    loan_df = pd.DataFrame(loans)

    return loan_df


def validate_loans(
    loan_df: pd.DataFrame,
    customer_file: str = "data/raw/customers.csv",
    vehicle_file: str = "data/raw/vehicles.csv",
) -> None:

    customer_df = pd.read_csv(customer_file)

    vehicle_df = pd.read_csv(vehicle_file)

    valid_customer_ids = set(
        customer_df["customer_id"]
    )

    valid_vehicle_ids = set(
        vehicle_df["vehicle_id"]
    )

    valid_dealer_ids = set(
        vehicle_df["dealer_id"]
    )

    vehicle_dealer_map = dict(
        zip(
            vehicle_df["vehicle_id"],
            vehicle_df["dealer_id"],
        )
    )

    if loan_df.empty:
        raise ValueError("Loan dataset is empty.")

    if loan_df["loan_id"].isnull().any():
        raise ValueError(
            "Loan dataset contains missing loan IDs."
        )

    if loan_df["loan_id"].duplicated().any():
        raise ValueError(
            "Loan dataset contains duplicate loan IDs."
        )

    if not loan_df["customer_id"].isin(
        valid_customer_ids
    ).all():
        raise ValueError(
            "Loan dataset contains invalid customer IDs."
        )

    if not loan_df["vehicle_id"].isin(
        valid_vehicle_ids
    ).all():
        raise ValueError(
            "Loan dataset contains invalid vehicle IDs."
        )

    if loan_df["vehicle_id"].duplicated().any():
        raise ValueError(
            "A vehicle is linked to more than one loan."
        )

    if not loan_df["dealer_id"].isin(
        valid_dealer_ids
    ).all():
        raise ValueError(
            "Loan dataset contains invalid dealer IDs."
        )

    for vehicle_id, dealer_id in zip(
        loan_df["vehicle_id"],
        loan_df["dealer_id"],
    ):
        if vehicle_dealer_map[vehicle_id] != dealer_id:
            raise ValueError(
                f"Dealer mismatch for vehicle {vehicle_id}."
            )

    if (
        loan_df["down_payment"] < 0
    ).any():
        raise ValueError(
            "Loan dataset contains negative down payments."
        )

    if (
        loan_df["down_payment"]
        >= loan_df["original_price"]
    ).any():
        raise ValueError(
            "Down payment must be less than original price."
        )

    if (
        loan_df["loan_amount"] <= 0
    ).any():
        raise ValueError(
            "Loan dataset contains invalid loan amounts."
        )

    if not loan_df["term_months"].isin(
        LOAN_TERMS
    ).all():
        raise ValueError(
            "Loan dataset contains invalid loan terms."
        )

    if not loan_df[
        "annual_interest_rate"
    ].between(
        4.50,
        10.50,
    ).all():
        raise ValueError(
            "Loan dataset contains invalid interest rates."
        )

    if (
        loan_df["monthly_payment"] <= 0
    ).any():
        raise ValueError(
            "Loan dataset contains invalid monthly payments."
        )

    if not loan_df["loan_status"].isin(
        LOAN_STATUSES
    ).all():
        raise ValueError(
            "Loan dataset contains invalid loan statuses."
        )

    if (
        pd.to_datetime(loan_df["maturity_date"])
        <= pd.to_datetime(
            loan_df["loan_start_date"]
        )
    ).any():
        raise ValueError(
            "Loan maturity date must be after start date."
        )

    print("Loan data validation passed.")


if __name__ == "__main__":
    df = generate_loans(1200)

    validate_loans(df)

    df.to_csv(
        "data/raw/loans.csv",
        index=False,
    )

    print(df.head())

    print(f"\nGenerated {len(df)} loans.")