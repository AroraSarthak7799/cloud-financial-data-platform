import random
import string
from datetime import date

import pandas as pd


random.seed(42)


VEHICLE_CATALOG = {
    "Freightliner": {
        "Cascadia": 165000,
        "M2 106": 125000,
    },
    "Western Star": {
        "49X": 190000,
        "47X": 175000,
    },
    "Volvo": {
        "VNL": 180000,
        "VNR": 155000,
    },
    "Kenworth": {
        "T680": 185000,
        "T880": 195000,
    },
    "Peterbilt": {
        "579": 190000,
        "567": 200000,
    },
}


VEHICLE_TYPES = [
    "Highway Tractor",
    "Vocational Truck",
    "Medium Duty Truck",
]


def generate_vin_like() -> str:
    allowed_characters = (
        string.ascii_uppercase.replace("I", "").replace("O", "").replace("Q", "")
        + string.digits
    )

    return "".join(
        random.choice(allowed_characters)
        for _ in range(17)
    )


def generate_vehicles(
    number_of_vehicles: int,
    dealer_file: str = "data/raw/dealers.csv",
) -> pd.DataFrame:

    dealer_df = pd.read_csv(dealer_file)

    dealer_ids = dealer_df["dealer_id"].tolist()

    vehicles = []

    current_year = date.today().year

    for vehicle_number in range(1, number_of_vehicles + 1):
        make = random.choice(list(VEHICLE_CATALOG.keys()))

        model = random.choice(
            list(VEHICLE_CATALOG[make].keys())
        )

        base_price = VEHICLE_CATALOG[make][model]

        model_year = random.randint(
            current_year - 8,
            current_year,
        )

        vehicle_age = current_year - model_year

        estimated_value = base_price * (0.92 ** vehicle_age)

        vehicle = {
            "vehicle_id": f"VEH{vehicle_number:06d}",
            "vin": generate_vin_like(),
            "dealer_id": random.choice(dealer_ids),
            "make": make,
            "model": model,
            "vehicle_type": random.choice(VEHICLE_TYPES),
            "model_year": model_year,
            "original_price": base_price,
            "estimated_value": round(estimated_value, 2),
        }

        vehicles.append(vehicle)

    vehicle_df = pd.DataFrame(vehicles)

    return vehicle_df


def validate_vehicles(
    vehicle_df: pd.DataFrame,
    dealer_file: str = "data/raw/dealers.csv",
) -> None:

    dealer_df = pd.read_csv(dealer_file)

    valid_dealer_ids = set(dealer_df["dealer_id"])

    if vehicle_df.empty:
        raise ValueError("Vehicle dataset is empty.")

    if vehicle_df["vehicle_id"].isnull().any():
        raise ValueError("Vehicle dataset contains missing vehicle IDs.")

    if vehicle_df["vehicle_id"].duplicated().any():
        raise ValueError("Vehicle dataset contains duplicate vehicle IDs.")

    if vehicle_df["vin"].isnull().any():
        raise ValueError("Vehicle dataset contains missing VINs.")

    if vehicle_df["vin"].duplicated().any():
        raise ValueError("Vehicle dataset contains duplicate VINs.")

    if not vehicle_df["vin"].str.len().eq(17).all():
        raise ValueError("Vehicle dataset contains invalid VIN lengths.")

    if vehicle_df["dealer_id"].isnull().any():
        raise ValueError("Vehicle dataset contains missing dealer IDs.")

    if not vehicle_df["dealer_id"].isin(valid_dealer_ids).all():
        raise ValueError(
            "Vehicle dataset contains dealer IDs that do not exist."
        )

    if not vehicle_df["make"].isin(VEHICLE_CATALOG.keys()).all():
        raise ValueError("Vehicle dataset contains invalid makes.")

    if not vehicle_df["vehicle_type"].isin(VEHICLE_TYPES).all():
        raise ValueError("Vehicle dataset contains invalid vehicle types.")

    current_year = date.today().year

    if not vehicle_df["model_year"].between(
        current_year - 8,
        current_year,
    ).all():
        raise ValueError("Vehicle dataset contains invalid model years.")

    if (vehicle_df["original_price"] <= 0).any():
        raise ValueError(
            "Vehicle dataset contains invalid original prices."
        )

    if (vehicle_df["estimated_value"] <= 0).any():
        raise ValueError(
            "Vehicle dataset contains invalid estimated values."
        )

    if (
        vehicle_df["estimated_value"]
        > vehicle_df["original_price"]
    ).any():
        raise ValueError(
            "Estimated vehicle value exceeds original price."
        )

    for make, model in zip(
        vehicle_df["make"],
        vehicle_df["model"],
    ):
        if model not in VEHICLE_CATALOG[make]:
            raise ValueError(
                f"Invalid make/model combination: {make}, {model}"
            )

    print("Vehicle data validation passed.")


if __name__ == "__main__":
    df = generate_vehicles(1500)

    validate_vehicles(df)

    df.to_csv(
        "data/raw/vehicles.csv",
        index=False,
    )

    print(df.head())

    print(f"\nGenerated {len(df)} vehicles.")