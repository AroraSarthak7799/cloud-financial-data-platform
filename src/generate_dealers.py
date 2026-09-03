from faker import Faker
import pandas as pd
import random


Faker.seed(42)
random.seed(42)

fake = Faker("en_CA")


PROVINCE_CITIES = {
    "Ontario": ["Toronto", "Mississauga", "Ottawa", "Hamilton"],
    "Quebec": ["Montreal", "Quebec City", "Laval"],
    "British Columbia": ["Vancouver", "Surrey", "Victoria"],
    "Alberta": ["Calgary", "Edmonton", "Red Deer"],
    "Manitoba": ["Winnipeg", "Brandon"],
    "Saskatchewan": ["Saskatoon", "Regina"],
    "Nova Scotia": ["Halifax", "Sydney"],
    "New Brunswick": ["Moncton", "Fredericton"],
    "Newfoundland and Labrador": ["St. John's", "Corner Brook"],
    "Prince Edward Island": ["Charlottetown", "Summerside"],
}


DEALER_TYPES = [
    "Franchise",
    "Independent",
    "Fleet",
]


def generate_dealers(number_of_dealers: int) -> pd.DataFrame:
    dealers = []

    for dealer_number in range(1, number_of_dealers + 1):
        province = random.choice(list(PROVINCE_CITIES.keys()))
        city = random.choice(PROVINCE_CITIES[province])

        dealer = {
            "dealer_id": f"DLR{dealer_number:04d}",
            "dealer_name": fake.company(),
            "dealer_type": random.choice(DEALER_TYPES),
            "city": city,
            "province": province,
            "postal_code": fake.postcode(),
            "phone_number": fake.phone_number(),
            "onboarding_date": fake.date_between(
                start_date="-10y",
                end_date="today",
            ),
            "active_flag": random.choice(["Y", "Y", "Y", "N"]),
        }

        dealers.append(dealer)

    dealer_df = pd.DataFrame(dealers)

    return dealer_df


def validate_dealers(dealer_df: pd.DataFrame) -> None:
    if dealer_df.empty:
        raise ValueError("Dealer dataset is empty.")

    if dealer_df["dealer_id"].isnull().any():
        raise ValueError("Dealer dataset contains missing dealer IDs.")

    if dealer_df["dealer_id"].duplicated().any():
        raise ValueError("Dealer dataset contains duplicate dealer IDs.")

    if dealer_df["province"].isnull().any():
        raise ValueError("Dealer dataset contains missing provinces.")

    if not dealer_df["province"].isin(PROVINCE_CITIES.keys()).all():
        raise ValueError("Dealer dataset contains invalid provinces.")

    if not dealer_df["dealer_type"].isin(DEALER_TYPES).all():
        raise ValueError("Dealer dataset contains invalid dealer types.")

    if not dealer_df["active_flag"].isin(["Y", "N"]).all():
        raise ValueError("Dealer dataset contains invalid active flags.")

    for province, city in zip(dealer_df["province"], dealer_df["city"]):
        if city not in PROVINCE_CITIES[province]:
            raise ValueError(
                f"Invalid city/province combination: {city}, {province}"
            )
        
    print("Dealer data validation passed.")


if __name__ == "__main__":
    df = generate_dealers(250)

    validate_dealers(df)

    df.to_csv("data/raw/dealers.csv", index=False)

    print(df.head())

    print(f"\nGenerated {len(df)} dealers.")