import pandas as pd
import pytest

from src.generate_dealers import (
    DEALER_TYPES,
    PROVINCE_CITIES,
    generate_dealers,
    validate_dealers,
)


def test_generate_dealers_returns_expected_number_of_rows():
    dealer_df = generate_dealers(25)

    assert len(dealer_df) == 25


def test_generated_dealers_have_valid_city_province_combinations():
    dealer_df = generate_dealers(100)

    for province, city in zip(
        dealer_df["province"],
        dealer_df["city"],
    ):
        assert city in PROVINCE_CITIES[province]


def test_validate_dealers_rejects_invalid_dealer_type():
    dealer_df = pd.DataFrame(
        {
            "dealer_id": ["DLR0001"],
            "province": ["Ontario"],
            "city": ["Toronto"],
            "dealer_type": ["Invalid Type"],
            "active_flag": ["Y"],
        }
    )

    with pytest.raises(
        ValueError,
        match="invalid dealer types",
    ):
        validate_dealers(dealer_df)


def test_validate_dealers_rejects_invalid_city_province_combination():
    dealer_df = pd.DataFrame(
        {
            "dealer_id": ["DLR0001"],
            "province": ["Ontario"],
            "city": ["Vancouver"],
            "dealer_type": [DEALER_TYPES[0]],
            "active_flag": ["Y"],
        }
    )

    with pytest.raises(
        ValueError,
        match="Invalid city/province combination",
    ):
        validate_dealers(dealer_df)