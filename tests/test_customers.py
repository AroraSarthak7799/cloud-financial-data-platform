import pandas as pd
import pytest

from src.generate_customers import (
    generate_customers,
    validate_customers,
)


def test_generate_customers_returns_expected_number_of_rows():
    customer_df = generate_customers(10)

    assert len(customer_df) == 10


def test_generate_customers_creates_unique_customer_ids():
    customer_df = generate_customers(100)

    assert customer_df["customer_id"].is_unique


def test_validate_customers_rejects_duplicate_customer_ids():
    customer_df = pd.DataFrame(
        {
            "customer_id": [
                "CUST00001",
                "CUST00001",
            ],
            "customer_name": [
                "Company A",
                "Company B",
            ],
            "created_date": [
                "2025-01-01",
                "2025-01-02",
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="duplicate customer IDs",
    ):
        validate_customers(customer_df)