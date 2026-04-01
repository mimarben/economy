# utils/schema_exporter.py
from enum import Enum
from typing import get_origin, get_args, Union
from pydantic import BaseModel

def resolve_type(annotation):
    """Resuelve Optional[...]"""
    if get_origin(annotation) is Union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        return args[0] if args else str
    return annotation


def map_type(py_type):
    if py_type == str:
        return "text"
    if py_type == int or py_type == float:
        return "number"
    if py_type == bool:
        return "checkbox"
    if isinstance(py_type, type) and issubclass(py_type, Enum):
        return "select"
    return "text"


def export_schema(model: type[BaseModel]):
    fields = []

    for name, field in model.model_fields.items():
        annotation = resolve_type(field.annotation)
        field_type = map_type(annotation)

        field_dict = {
            "key": name,
            "label": field.title or name.replace("_", " ").title(),
            "type": field_type,
            "required": field.is_required()
        }

        # ENUM → options
        if field_type == "select" and isinstance(annotation, type) and issubclass(annotation, Enum):
            field_dict["options"] = [
                {"value": e.value, "label": str(e.value).capitalize()}
                for e in annotation
            ]

        fields.append(field_dict)

    return {
        "model": model.__name__,
        "fields": fields
    }