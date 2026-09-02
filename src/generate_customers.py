from faker import Faker
import pandas as pd


Faker.seed(42)
fake = Faker("en_CA")


def generate_customers(number_of_customers: int) -> pd.DataFrame:
    customers = []

    for customer_number in range(1, number_of_customers + 1):
        customer = {
            "customer_id": f"CUST{customer_number:05d}",
            "customer_name": fake.company(),
            "email": fake.company_email(),
            "phone_number": fake.phone_number(),
            "city": fake.city(),
            "province": fake.province(),
            "postal_code": fake.postcode(),
            "created_date": fake.date_between(
                start_date="-5y",
                end_date="today"
            ),
        }

        customers.append(customer)

    customer_df = pd.DataFrame(customers)

    return customer_df


def validate_customers(customer_df: pd.DataFrame) -> None:
    if customer_df.empty:
        raise ValueError("Customer dataset is empty.")

    if customer_df["customer_id"].isnull().any():
        raise ValueError("Customer dataset contains missing customer IDs.")

    if customer_df["customer_id"].duplicated().any():
        raise ValueError("Customer dataset contains duplicate customer IDs.")

    if customer_df["customer_name"].isnull().any():
        raise ValueError("Customer dataset contains missing customer names.")

    if customer_df["created_date"].isnull().any():
        raise ValueError("Customer dataset contains missing created dates.")

    print("Customer data validation passed.")


if __name__ == "__main__":
    df = generate_customers(1000)

    validate_customers(df)

    df.to_csv("data/raw/customers.csv", index=False)

    print(df.head())

    print(f"\nGenerated {len(df)} customers.")