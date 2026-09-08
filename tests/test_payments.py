from datetime import date

import pandas as pd
import pytest

from src.generate_payments import (
    generate_payments,
    validate_payments,
)


def create_test_loan_file(tmp_path):
    today = pd.Timestamp(date.today())

    loan_df = pd.DataFrame(
        {
            "loan_id": [
                "LOAN000001",
                "LOAN000002",
            ],
            "monthly_payment": [
                2500.00,
                3200.00,
            ],
            "loan_status": [
                "Active",
                "Delinquent",
            ],
            "loan_start_date": [
                (today - pd.DateOffset(months=6)).date(),
                (today - pd.DateOffset(months=4)).date(),
            ],
            "maturity_date": [
                (today + pd.DateOffset(months=54)).date(),
                (today + pd.DateOffset(months=56)).date(),
            ],
        }
    )

    loan_file = tmp_path / "loans.csv"

    loan_df.to_csv(
        loan_file,
        index=False,
    )

    return loan_file


def test_generate_payments_creates_payment_records(
    tmp_path,
):
    loan_file = create_test_loan_file(
        tmp_path
    )

    payment_df = generate_payments(
        loan_file=str(loan_file)
    )

    assert len(payment_df) > 0


def test_generated_payments_reference_valid_loans(
    tmp_path,
):
    loan_file = create_test_loan_file(
        tmp_path
    )

    payment_df = generate_payments(
        loan_file=str(loan_file)
    )

    valid_loan_ids = {
        "LOAN000001",
        "LOAN000002",
    }

    assert payment_df[
        "loan_id"
    ].isin(
        valid_loan_ids
    ).all()


def test_generated_payments_have_unique_loan_payment_numbers(
    tmp_path,
):
    loan_file = create_test_loan_file(
        tmp_path
    )

    payment_df = generate_payments(
        loan_file=str(loan_file)
    )

    assert not payment_df.duplicated(
        subset=[
            "loan_id",
            "payment_number",
        ]
    ).any()


def test_validate_payments_rejects_missed_payment_with_amount(
    tmp_path,
):
    loan_file = create_test_loan_file(
        tmp_path
    )

    today = pd.Timestamp(date.today())

    payment_df = pd.DataFrame(
        {
            "payment_id": [
                "PAY00000001"
            ],
            "loan_id": [
                "LOAN000001"
            ],
            "payment_number": [
                1
            ],
            "scheduled_payment_date": [
                (
                    today
                    - pd.DateOffset(months=5)
                ).date()
            ],
            "actual_payment_date": [
                None
            ],
            "scheduled_amount": [
                2500.00
            ],
            "payment_amount": [
                1000.00
            ],
            "payment_status": [
                "Missed"
            ],
            "days_late": [
                30
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="Missed payments must have a zero payment amount",
    ):
        validate_payments(
            payment_df,
            loan_file=str(loan_file),
        )