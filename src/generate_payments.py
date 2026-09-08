import random
from datetime import date, timedelta

import pandas as pd


random.seed(42)


PAYMENT_STATUSES = [
    "On Time",
    "Late",
    "Partial",
    "Missed",
]


PAYMENT_STATUS_WEIGHTS = {
    "Active": {
        "On Time": 90,
        "Late": 7,
        "Partial": 2,
        "Missed": 1,
    },
    "Paid Off": {
        "On Time": 95,
        "Late": 5,
    },
    "Delinquent": {
        "On Time": 55,
        "Late": 25,
        "Partial": 12,
        "Missed": 8,
    },
    "Defaulted": {
        "On Time": 35,
        "Late": 20,
        "Partial": 15,
        "Missed": 30,
    },
}


def choose_payment_status(loan_status: str) -> str:
    if loan_status not in PAYMENT_STATUS_WEIGHTS:
        raise ValueError(
            f"Unknown loan status: {loan_status}"
        )

    status_weights = PAYMENT_STATUS_WEIGHTS[
        loan_status
    ]

    return random.choices(
        population=list(status_weights.keys()),
        weights=list(status_weights.values()),
        k=1,
    )[0]


def generate_payments(
    loan_file: str = "data/raw/loans.csv",
) -> pd.DataFrame:

    loan_df = pd.read_csv(loan_file)

    payments = []

    payment_counter = 1

    today = pd.Timestamp(date.today())

    for _, loan in loan_df.iterrows():
        loan_id = loan["loan_id"]

        monthly_payment = float(
            loan["monthly_payment"]
        )

        loan_status = loan["loan_status"]

        loan_start_date = pd.Timestamp(
            loan["loan_start_date"]
        )

        maturity_date = pd.Timestamp(
            loan["maturity_date"]
        )

        end_date = min(
            today,
            maturity_date,
        )

        payment_number = 1

        scheduled_date = (
            loan_start_date
            + pd.DateOffset(months=payment_number)
        )

        while scheduled_date <= end_date:
            payment_status = choose_payment_status(
                loan_status
            )

            days_since_due = (
                today - scheduled_date
            ).days

            if (
                payment_status == "Late"
                and days_since_due <= 0
            ):
                payment_status = "On Time"

            if payment_status == "On Time":
                actual_payment_date = (
                    scheduled_date
                    - timedelta(
                        days=random.randint(0, 3)
                    )
                )

                payment_amount = monthly_payment

                days_late = 0

            elif payment_status == "Late":
                maximum_late_days = min(
                    30,
                    days_since_due,
                )

                late_days = random.randint(
                    1,
                    maximum_late_days,
                )

                actual_payment_date = (
                    scheduled_date
                    + timedelta(days=late_days)
                )

                payment_amount = monthly_payment

                days_late = late_days

            elif payment_status == "Partial":
                maximum_delay = max(
                    0,
                    min(
                        20,
                        days_since_due,
                    ),
                )

                if maximum_delay > 0:
                    late_days = random.randint(
                        0,
                        maximum_delay,
                    )
                else:
                    late_days = 0

                actual_payment_date = (
                    scheduled_date
                    + timedelta(days=late_days)
                )

                payment_amount = round(
                    monthly_payment
                    * random.uniform(
                        0.40,
                        0.90,
                    ),
                    2,
                )

                days_late = late_days

            else:
                actual_payment_date = None

                payment_amount = 0.0

                days_late = max(
                    days_since_due,
                    0,
                )

            payment = {
                "payment_id": (
                    f"PAY{payment_counter:08d}"
                ),
                "loan_id": loan_id,
                "payment_number": payment_number,
                "scheduled_payment_date": (
                    scheduled_date.date()
                ),
                "actual_payment_date": (
                    actual_payment_date.date()
                    if actual_payment_date is not None
                    else None
                ),
                "scheduled_amount": (
                    monthly_payment
                ),
                "payment_amount": (
                    payment_amount
                ),
                "payment_status": (
                    payment_status
                ),
                "days_late": days_late,
            }

            payments.append(payment)

            payment_counter += 1

            payment_number += 1

            scheduled_date = (
                loan_start_date
                + pd.DateOffset(
                    months=payment_number
                )
            )

    payment_df = pd.DataFrame(payments)

    return payment_df


def validate_payments(
    payment_df: pd.DataFrame,
    loan_file: str = "data/raw/loans.csv",
) -> None:

    loan_df = pd.read_csv(loan_file)

    valid_loan_ids = set(
        loan_df["loan_id"]
    )

    loan_payment_map = dict(
        zip(
            loan_df["loan_id"],
            loan_df["monthly_payment"],
        )
    )

    loan_start_map = dict(
        zip(
            loan_df["loan_id"],
            loan_df["loan_start_date"],
        )
    )

    loan_maturity_map = dict(
        zip(
            loan_df["loan_id"],
            loan_df["maturity_date"],
        )
    )

    if payment_df.empty:
        raise ValueError(
            "Payment dataset is empty."
        )

    if payment_df["payment_id"].isnull().any():
        raise ValueError(
            "Payment dataset contains missing payment IDs."
        )

    if payment_df["payment_id"].duplicated().any():
        raise ValueError(
            "Payment dataset contains duplicate payment IDs."
        )

    if payment_df["loan_id"].isnull().any():
        raise ValueError(
            "Payment dataset contains missing loan IDs."
        )

    if not payment_df["loan_id"].isin(
        valid_loan_ids
    ).all():
        raise ValueError(
            "Payment dataset contains invalid loan IDs."
        )

    if (
        payment_df["payment_number"] <= 0
    ).any():
        raise ValueError(
            "Payment dataset contains invalid payment numbers."
        )

    if payment_df.duplicated(
        subset=[
            "loan_id",
            "payment_number",
        ]
    ).any():
        raise ValueError(
            "Duplicate payment numbers exist for a loan."
        )

    if not payment_df["payment_status"].isin(
        PAYMENT_STATUSES
    ).all():
        raise ValueError(
            "Payment dataset contains invalid payment statuses."
        )

    if (
        payment_df["scheduled_amount"] <= 0
    ).any():
        raise ValueError(
            "Payment dataset contains invalid scheduled amounts."
        )

    if (
        payment_df["payment_amount"] < 0
    ).any():
        raise ValueError(
            "Payment dataset contains negative payment amounts."
        )

    expected_amounts = payment_df[
        "loan_id"
    ].map(
        loan_payment_map
    )

    if not (
        payment_df["scheduled_amount"].round(2)
        == expected_amounts.round(2)
    ).all():
        raise ValueError(
            "Scheduled payment does not match loan payment amount."
        )

    scheduled_dates = pd.to_datetime(
        payment_df["scheduled_payment_date"]
    )

    actual_dates = pd.to_datetime(
        payment_df["actual_payment_date"],
        errors="coerce",
    )

    loan_start_dates = pd.to_datetime(
        payment_df["loan_id"].map(
            loan_start_map
        )
    )

    maturity_dates = pd.to_datetime(
        payment_df["loan_id"].map(
            loan_maturity_map
        )
    )

    today = pd.Timestamp(date.today())

    if (
        scheduled_dates <= loan_start_dates
    ).any():
        raise ValueError(
            "Payment date must be after loan start date."
        )

    if (
        scheduled_dates > maturity_dates
    ).any():
        raise ValueError(
            "Payment date exceeds loan maturity date."
        )

    if (
        scheduled_dates > today
    ).any():
        raise ValueError(
            "Payment dataset contains future scheduled payments."
        )

    missed_mask = (
        payment_df["payment_status"]
        == "Missed"
    )

    if actual_dates[
        missed_mask
    ].notna().any():
        raise ValueError(
            "Missed payments cannot have an actual payment date."
        )

    if (
        payment_df.loc[
            missed_mask,
            "payment_amount",
        ] != 0
    ).any():
        raise ValueError(
            "Missed payments must have a zero payment amount."
        )

    non_missed_mask = ~missed_mask

    if actual_dates[
        non_missed_mask
    ].isna().any():
        raise ValueError(
            "Received payments must have an actual payment date."
        )

    on_time_mask = (
        payment_df["payment_status"]
        == "On Time"
    )

    if (
        actual_dates[on_time_mask]
        > scheduled_dates[on_time_mask]
    ).any():
        raise ValueError(
            "On-time payments cannot occur after the scheduled date."
        )

    late_mask = (
        payment_df["payment_status"]
        == "Late"
    )

    if (
        actual_dates[late_mask]
        <= scheduled_dates[late_mask]
    ).any():
        raise ValueError(
            "Late payments must occur after the scheduled date."
        )

    partial_mask = (
        payment_df["payment_status"]
        == "Partial"
    )

    if (
        payment_df.loc[
            partial_mask,
            "payment_amount",
        ] <= 0
    ).any():
        raise ValueError(
            "Partial payments must be greater than zero."
        )

    if (
        payment_df.loc[
            partial_mask,
            "payment_amount",
        ]
        >= payment_df.loc[
            partial_mask,
            "scheduled_amount",
        ]
    ).any():
        raise ValueError(
            "Partial payments must be less than the scheduled amount."
        )

    full_payment_mask = payment_df[
        "payment_status"
    ].isin(
        [
            "On Time",
            "Late",
        ]
    )

    if not (
        payment_df.loc[
            full_payment_mask,
            "payment_amount",
        ].round(2)
        == payment_df.loc[
            full_payment_mask,
            "scheduled_amount",
        ].round(2)
    ).all():
        raise ValueError(
            "Full payments must equal the scheduled amount."
        )

    if (
        payment_df["days_late"] < 0
    ).any():
        raise ValueError(
            "Payment dataset contains negative days late."
        )

    print("Payment data validation passed.")


if __name__ == "__main__":
    df = generate_payments()

    validate_payments(df)

    df.to_csv(
        "data/raw/payments.csv",
        index=False,
    )

    print(df.head())

    print(
        f"\nGenerated {len(df)} payments."
    )