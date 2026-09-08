from datetime import date

import pandas as pd
import pytest

from src.generate_vehicles import (
    VEHICLE_CATALOG,
    VEHICLE_TYPES,
    generate_vehicles,
    validate_vehicles,
)


def create_test_dealer_file(tmp_path):
    dealer_df = pd.DataFrame(
        {
            "dealer_id": [
                "DLR0001",
                "DLR0002",
                "DLR0003",
            ]
        }
    )

    dealer_file = tmp_path / "dealers.csv"

    dealer_df.to_csv(
        dealer_file,
        index=False,
    )

    return dealer_file


def test_generate_vehicles_returns_expected_number_of_rows(
    tmp_path,
):
    dealer_file = create_test_dealer_file(
        tmp_path
    )

    vehicle_df = generate_vehicles(
        20,
        dealer_file=str(dealer_file),
    )

    assert len(vehicle_df) == 20


def test_generated_vehicles_have_valid_dealer_ids(
    tmp_path,
):
    dealer_file = create_test_dealer_file(
        tmp_path
    )

    vehicle_df = generate_vehicles(
        50,
        dealer_file=str(dealer_file),
    )

    valid_dealer_ids = {
        "DLR0001",
        "DLR0002",
        "DLR0003",
    }

    assert vehicle_df[
        "dealer_id"
    ].isin(
        valid_dealer_ids
    ).all()


def test_generated_vehicles_have_valid_vins(
    tmp_path,
):
    dealer_file = create_test_dealer_file(
        tmp_path
    )

    vehicle_df = generate_vehicles(
        100,
        dealer_file=str(dealer_file),
    )

    assert vehicle_df["vin"].is_unique

    assert vehicle_df[
        "vin"
    ].str.len().eq(17).all()


def test_validate_vehicles_rejects_invalid_make_model_combination(
    tmp_path,
):
    dealer_file = create_test_dealer_file(
        tmp_path
    )

    current_year = date.today().year

    vehicle_df = pd.DataFrame(
        {
            "vehicle_id": [
                "VEH000001"
            ],
            "vin": [
                "ABCDEFGHJKLMN1234"
            ],
            "dealer_id": [
                "DLR0001"
            ],
            "make": [
                "Volvo"
            ],
            "model": [
                "Cascadia"
            ],
            "vehicle_type": [
                VEHICLE_TYPES[0]
            ],
            "model_year": [
                current_year
            ],
            "original_price": [
                180000
            ],
            "estimated_value": [
                180000
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="Invalid make/model combination",
    ):
        validate_vehicles(
            vehicle_df,
            dealer_file=str(dealer_file),
        )