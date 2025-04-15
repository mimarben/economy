import os
from sqlalchemy import create_engine

db_path = "../../db/economy.db"
db_dir = os.path.dirname(db_path)
if not os.path.exists(db_dir):
    print(f"Directory {db_dir} NOT exists.")
else:
    print(f"Directory {db_dir} already exists.")


# Construct the database URL
db_url = f"sqlite:///{os.path.abspath(db_path)}"

# Create the engine
try:
    engine = create_engine(db_url, echo=True)
    connection = engine.connect()
    print("Database connection successful!")
except Exception as e:
    print(f"Error connecting to the database: {e}")
finally:
    if 'connection' in locals():
        connection.close()