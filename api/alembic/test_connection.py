from sqlalchemy import create_engine

engine = create_engine("sqlite:///../../db/economy.db", echo=True)
connection = engine.connect()
print("Database connection successful!")
connection.close()