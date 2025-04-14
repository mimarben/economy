# Ruta para actualizar información de un artículo
from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Ruta raíz
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup
DATABASE_URL = "sqlite:///./db/economy.db"  # SQLite database file
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Pydantic model for user input
class UserCreate(BaseModel):
    name: str
    description: str

# Ruta raíz
@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# Ruta para obtener información de un usuario por ID
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.id, "name": user.name, "description": user.description}

# Ruta para crear un nuevo usuario
@app.post("/users/", response_model=UserCreate)
async def create_user(user: UserCreate):
    db: Session = SessionLocal()
    new_user = User(name=user.name, description=user.description)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return new_user

# Ruta para actualizar un usuario
@app.put("/users/{user_id}", response_model=UserCreate)
async def update_user(user_id: int, user: UserCreate):
    db: Session = SessionLocal()
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.name = user.name
    db_user.description = user.description
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
