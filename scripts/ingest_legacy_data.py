from pathlib import Path
import pandas as pd  # pyright: ignore[reportMissingModuleSource]
import os
from sqlalchemy import create_engine  # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

# Load environment variables
load_dotenv()

# Path to my CSV file
csv_file = "../data/raw/dynamic_supply_chain_logistics_dataset.csv"  # My CSV path
db_host = os.getenv("db_host", "localhost")  # Running from My host machine
db_port = "5433"  # Port you published in docker-compose.yml (or 5432 if different)
db_name = "cold-chain-postgres"  # My database name
db_user = "me"  # My PostgreSQL user
table_name = "cold_chain_shipments"  # Table to create

db_password = os.environ["POSTGRES_PASSWORD"]

# Create connection string for PostgreSQL
# This line creates a Connection URI (Uniform Resource Identifier), which is a standardized string that tells SQLAlchemy exactly how, where, and with what credentials to connect to My database.
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Connect to PostgreSQL
print(f"Connecting to PostgreSQL at {db_host}:{db_port}...")
engine = create_engine(connection_string)

# Read CSV file
print(f"Reading CSV from {csv_file}...")
df = pd.read_csv(csv_file)
print(f"Loaded {len(df)} rows")

# Insert into table
table_name = "supply_chain_data"  # ← Change this to My desired table name
print(f"Inserting into table '{table_name}'...")
df.to_sql(table_name, engine, if_exists='replace', index=False)

print("✅ Data loaded successfully!")
