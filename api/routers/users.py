# routes.py
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from models.models import User
from schemas.users import UserCreate, UserRead, UserUpdate
from pydantic import ValidationError
from db.database import get_db

router = Blueprint("users", __name__)

@router.post("/users")
def create_user():
    db = next(get_db())
    try:
        user_data = UserCreate(**request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    new_user = User(**user_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return jsonify(UserRead.from_orm(new_user).dict())


@router.get("/users/<int:user_id>")
def get_user(user_id):
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(UserRead.from_orm(user).dict())


@router.patch("/users/<int:user_id>")
def update_user(user_id):
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        user_data = UserUpdate(**request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return jsonify(UserRead.from_orm(user).dict())


@router.get("/users")
def list_users():
    db = next(get_db())
    users = db.query(User).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    user_data = [UserRead.model_validate(u).model_dump() for u in users]
    return jsonify(user_data)
