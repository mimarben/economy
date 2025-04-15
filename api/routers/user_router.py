# routes.py
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _

from models.models import User
from api.schemas.user_schema import UserCreate, UserRead, UserUpdate
from db.database import get_db
from services.user_service import UserService


router = Blueprint("users", __name__)

@router.post("/users")
def create_user():
    db = next(get_db())
    try:
        user_data = UserCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": _("INVALID_DATA"), "details": e.errors()}), 400
    if UserService.user_exists(db, user_data.dni):
        return jsonify({"error": _("DNI_EXIST"), "details": "None"}), 409
    new_user = User(**user_data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return jsonify(UserRead.model_validate(new_user).model_dump())


@router.get("/users/<int:user_id>")
def get_user(user_id):
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(UserRead.model_validate(user).model_dump())


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
    
    if user_data.dni and UserService.user_exists(db, user_data.dni, exclude_user_id=user.id):
        return jsonify({"error": "Another user already has this DNI"}), 409
    
    validated_data = user_data.model_dump(exclude_unset=True)
    for key, value in validated_data.items():
        setattr(user, key, value)


    db.commit()
    db.refresh(user)
    return jsonify(UserRead.model_validate(user).model_dump())


@router.get("/users")
def list_users():
    db = next(get_db())
    users = db.query(User).all()
    # Convert SQLAlchemy models to Pydantic UserRead and serialize
    user_data = [UserRead.model_validate(u).model_dump() for u in users]
    return jsonify(user_data)
