import json

import pytest

from services.core.response_service import Response
from utils.i18n import _, reset_locale, set_locale


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "The request could not be completed because of a database error."),
        ("es", "No se pudo completar la solicitud por un error de base de datos."),
    ],
)
def test_error_response_keeps_code_and_hides_raw_details(language, expected):
    locale_token = set_locale(language)
    try:
        response = Response.error("DATABASE_ERROR", "private database connection string", 500)
    finally:
        reset_locale(locale_token)

    body = json.loads(response.body)
    assert body == {"response": "DATABASE_ERROR", "details": expected}


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "email: This field is required."),
        ("es", "email: Este campo es obligatorio."),
    ],
)
def test_validation_details_are_localized_without_framework_messages(language, expected):
    locale_token = set_locale(language)
    try:
        response = Response.error(
            "VALIDATION_ERROR",
            [
                {
                    "loc": ("body", "email"),
                    "type": "missing",
                    "msg": "raw framework validation message",
                    "input": "private value",
                }
            ],
            400,
        )
    finally:
        reset_locale(locale_token)

    body = json.loads(response.body)
    assert body["response"] == "VALIDATION_ERROR"
    assert body["details"] == expected


def test_translated_message_uses_selected_locale():
    locale_token = set_locale("es")
    try:
        assert str(_("USER_FOUND")) == "Se encontró el usuario."
    finally:
        reset_locale(locale_token)
