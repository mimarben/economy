from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response as FastAPIResponse

from utils.i18n import _, is_message_key
# Setup logging
from services.logs.logger_service import setup_logger


_VALIDATION_MESSAGE_KEYS = {
    "missing": "VALIDATION_REQUIRED",
    "string_too_short": "VALIDATION_TOO_SHORT",
    "string_too_long": "VALIDATION_TOO_LONG",
    "value_error.email": "VALIDATION_INVALID_EMAIL",
    "int_parsing": "VALIDATION_INVALID_TYPE",
    "float_parsing": "VALIDATION_INVALID_TYPE",
    "bool_parsing": "VALIDATION_INVALID_TYPE",
    "string_type": "VALIDATION_INVALID_TYPE",
    "int_type": "VALIDATION_INVALID_TYPE",
    "float_type": "VALIDATION_INVALID_TYPE",
    "bool_type": "VALIDATION_INVALID_TYPE",
    "greater_than": "VALIDATION_OUT_OF_RANGE",
    "greater_than_equal": "VALIDATION_OUT_OF_RANGE",
    "less_than": "VALIDATION_OUT_OF_RANGE",
    "less_than_equal": "VALIDATION_OUT_OF_RANGE",
    "extra_forbidden": "VALIDATION_EXTRA_FIELD",
    "json_invalid": "VALIDATION_INVALID_JSON",
}


class Response:
    @staticmethod
    def _message_text(message, fallback_key: str) -> str:
        if isinstance(message, str):
            message_key = getattr(message, "key", message)
            if is_message_key(message_key):
                return str(message) if hasattr(message, "key") else _(message_key)
        return _(fallback_key)

    @staticmethod
    def _validation_details(errors: list) -> str:
        messages = []
        for error in errors:
            location = error.get("loc", ())
            field = ".".join(str(part) for part in location if part not in {"body", "query", "path", "header", "cookie"})
            message_key = _VALIDATION_MESSAGE_KEYS.get(error.get("type"), "VALIDATION_INVALID")
            message = _(message_key)
            messages.append(f"{field}: {message}" if field else str(message))
        return "\n".join(messages) or _("VALIDATION_ERROR")

    @staticmethod
    def _json(payload: dict, status_code: int, headers: dict | None = None):
        if status_code == 204:
            return FastAPIResponse(status_code=status_code, headers=headers)
        return JSONResponse(
            content=jsonable_encoder(payload),
            status_code=status_code,
            headers=headers,
        )

    @staticmethod
    def error(error: str, details, status_code: int, name: str = None, headers: dict | None = None):
        logger = setup_logger(name or "default_error_source")  # Use a default if name is None
        error_key = getattr(error, "key", error)
        if not is_message_key(error_key):
            error_key = "INTERNAL_ERROR"
        logger.error("Error: %s", _(error_key))

        # Server errors: log the raw cause, never leak it to the client.
        if status_code >= 500:
            logger.error("Internal error details: %r", details)
            details = _(error_key)
            return Response._json({
                "response": error_key,
                "details": details
            }, status_code, headers)

        if isinstance(details, list):
            details = Response._validation_details(details)
        else:
            details = Response._message_text(details, error_key)
        return Response._json({
            "response": error_key,
            "details": details
        }, status_code, headers)

    @staticmethod
    def ok(response, details: str, status_code: int, name: str = None):
        logger = setup_logger(name or "default_ok_source")  # Use a default if name is None
        details = Response._message_text(details, "UNEXPECTED_ERROR")
        logger.info("Response: %s", details)
        return Response._json({
            "response": response,
            "details": details
        }, status_code)

    @staticmethod
    def ok_data(response: str, details: str, status_code: int, name: str = None):
        """Alias of Response.ok, kept for backwards compatibility with existing callers."""
        return Response.ok(response, details, status_code, name)

    @staticmethod
    def ok_message(details: str, status_code: int, name: str = None):
        logger = setup_logger(name or "default_message_source")
        details = Response._message_text(details, "UNEXPECTED_ERROR")
        logger.info("Response: %s", details)
        return Response._json({
            "response": None,
            "details": details
        }, status_code)
