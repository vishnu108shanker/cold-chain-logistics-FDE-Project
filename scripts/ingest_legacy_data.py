from pathlib import Path
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Path to your CSV file
csv_file = "data/raw/your_dataset.csv"  # ← Change this to your actual CSV path

# Database connection details
db_host = "localhost"  # If running locally
# db_host = "postgres"  # If running from inside Docker Compose network
db_port = "5433"  # ← Change this to match your Compose port mapping (or 5432 if on same network)
db_name = "my_cold_chain_db"
db_user = "postgres"
db_password = os.getenv("POSTGRES_PASSWORD", "mysecretpassword")

# Create connection string for PostgreSQL
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Connect to PostgreSQL
print(f"Connecting to PostgreSQL at {db_host}:{db_port}...")
engine = create_engine(connection_string)

# Read CSV file
print(f"Reading CSV from {csv_file}...")
df = pd.read_csv(csv_file)
print(f"Loaded {len(df)} rows")

# Insert into table
table_name = "supply_chain_data"  # ← Change this to your desired table name
print(f"Inserting into table '{table_name}'...")
df.to_sql(table_name, engine, if_exists='replace', index=False)

print("✅ Data loaded successfully!")
