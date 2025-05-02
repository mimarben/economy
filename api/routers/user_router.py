# routes.py
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import Babel, _

from models.models import User
from schemas.user_schema import UserCreate, UserRead, UserUpdate
from db.database import get_db
from services.user_service import UserService
from services.response_service import Response


router = Blueprint("users", __name__)
name = "user router"
@router.post("/users")
def create_user():
    db = next(get_db())
    try:
        user_data = UserCreate.model_validate(request.json, context={"db": db})
    except ValidationError as e:
        return Response._error(_("INVALID_DATA"), e.errors(), 400, name)
    try:
      if UserService.user_exists(db, user_data.dni):
        return Response._error(_("DNI_EXIST"),_("NONE"), 409, name)
      new_user = User(**user_data.model_dump())
      db.add(new_user)
      db.commit()
      db.refresh(new_user)
      return Response._ok_data(UserRead.model_validate(new_user).model_dump(), _("USER_CREATED"), 201,name)
    except Exception as e:
        return Response._error(_("UNKNOW_ERROR"),e.errors(), 409, name)


@router.get("/users/<int:user_id>")
def get_user(user_id):
    db = next(get_db())
    try:
      user = db.query(User).filter(User.id == user_id).first()
      if not user:
            return Response._error(_("USER_NOT_FOUND"), _("USER_NOT_FOUND_DATABASE"), 404, name)
      return Response._ok_data(UserRead.model_validate(user).model_dump(), _("USER_FOUND"), 200, name)

    except Exception as e:
        return Response._error(_("UNKNOWN_ERROR"), e.error(), 500, name)


@router.patch("/users/<int:user_id>")
def update_user(user_id):
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return Response._error(_("USER_NOT_FOUND"), _("NOT_USER_ID") + f" {user_id}" , 404, name)
        # Validate incoming user data
        user_data = UserUpdate(**request.json)
        # Check for existing DNI
        if user_data.dni and UserService.user_exists(db, user_data.dni, exclude_user_id=user.id):
            return Response._error(_("DNI_EXIST"), _("DUPLICATED_DNI")+ f" {user_data.dni}", 409, name)

        # Update user attributes
        validated_data = user_data.model_dump(exclude_unset=True)
        for key, value in validated_data.items():
            setattr(user, key, value)

        # Commit changes to the database
        db.commit()
        db.refresh(user)
        return Response._ok_data(UserRead.model_validate(user).model_dump(), _("USER_UPDATED"), 200, name)

    except ValidationError as e:
        # Handle validation errors
        return Response._error(_("VALIDATION_ERROR"), e.error(), 400, name)

    except Exception as e:
        return Response._error(_("UNKNOWN_ERROR"), str(e), 500, name)


@router.get("/users")
def list_users():
    db = next(get_db())
    try:
        users = db.query(User).all()
        # Convertir modelos de SQLAlchemy a Pydantic UserRead y serializar
        user_data = [UserRead.model_validate(u).model_dump() for u in users]
        if not user_data:
            return Response._error(_("USER_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(user_data, _("USERS_FOUND"), 200, name)
    except Exception as e:
        return Response._error(_("UNKNOWN_ERROR"), e.error(), 500, name)

