import pandas as pd
import pytest

from src.generate_loans import (
    calculate_monthly_payment,
    generate_loans,
    validate_loans,
)


def create_test_customer_file(tmp_path):
    customer_df = pd.DataFrame(
        {
            "customer_id": [
                "CUST00001",
                "CUST00002",
                "CUST00003",
            ]
        }
    )

    customer_file = tmp_path / "customers.csv"

    customer_df.to_csv(
        customer_file,
        index=False,
    )

    return customer_file


def create_test_vehicle_file(tmp_path):
    vehicle_df = pd.DataFrame(
        {
            "vehicle_id": [
                "VEH000001",
                "VEH000002",
                "VEH000003",
            ],
            "dealer_id": [
                "DLR0001",
                "DLR0002",
                "DLR0003",
            ],
            "original_price": [
                150000,
                180000,
                200000,
            ],
        }
    )

    vehicle_file = tmp_path / "vehicles.csv"

    vehicle_df.to_csv(
        vehicle_file,
        index=False,
    )

    return vehicle_file


def test_generate_loans_returns_expected_number_of_rows(
    tmp_path,
):
    customer_file = create_test_customer_file(
        tmp_path
    )

    vehicle_file = create_test_vehicle_file(
        tmp_path
    )

    loan_df = generate_loans(
        3,
        customer_file=str(customer_file),
        vehicle_file=str(vehicle_file),
    )

    assert len(loan_df) == 3


def test_generated_loans_use_each_vehicle_only_once(
    tmp_path,
):
    customer_file = create_test_customer_file(
        tmp_path
    )

    vehicle_file = create_test_vehicle_file(
        tmp_path
    )

    loan_df = generate_loans(
        3,
        customer_file=str(customer_file),
        vehicle_file=str(vehicle_file),
    )

    assert loan_df["vehicle_id"].is_unique


def test_calculate_monthly_payment_returns_expected_value():
    monthly_payment = calculate_monthly_payment(
        loan_amount=100000,
        annual_interest_rate=6.0,
        term_months=60,
    )

    assert monthly_payment == 1933.28


def test_generate_loans_rejects_more_loans_than_vehicles(
    tmp_path,
):
    customer_file = create_test_customer_file(
        tmp_path
    )

    vehicle_file = create_test_vehicle_file(
        tmp_path
    )

    with pytest.raises(
        ValueError,
        match="cannot exceed number of available vehicles",
    ):
        generate_loans(
            4,
            customer_file=str(customer_file),
            vehicle_file=str(vehicle_file),
        )


def test_validate_loans_rejects_vehicle_dealer_mismatch(
    tmp_path,
):
    customer_file = create_test_customer_file(
        tmp_path
    )

    vehicle_file = create_test_vehicle_file(
        tmp_path
    )

    loan_df = pd.DataFrame(
        {
            "loan_id": [
                "LOAN000001"
            ],
            "customer_id": [
                "CUST00001"
            ],
            "vehicle_id": [
                "VEH000001"
            ],
            "dealer_id": [
                "DLR0002"
            ],
            "loan_start_date": [
                "2025-01-01"
            ],
            "maturity_date": [
                "2030-01-01"
            ],
            "original_price": [
                150000
            ],
            "down_payment": [
                30000
            ],
            "loan_amount": [
                120000
            ],
            "annual_interest_rate": [
                6.0
            ],
            "term_months": [
                60
            ],
            "monthly_payment": [
                2319.94
            ],
            "loan_status": [
                "Active"
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="Dealer mismatch",
    ):
        validate_loans(
            loan_df,
            customer_file=str(customer_file),
            vehicle_file=str(vehicle_file),
        )