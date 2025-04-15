import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_path = "../db/economy.db"




# Construct the database URL
db_url = f"sqlite:///{os.path.abspath(db_path)}"

engine = create_engine(db_url, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
        print("Database connection successful!")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
    finally:
        db.close()
    """ try:
        connection = engine.connect()
        print("Database connection successful!")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
    finally:
        if 'connection' in locals():
            connection.close() """