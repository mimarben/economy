from flask import jsonify
from flask_babel import _
class Response:
    def _error(error: str, details: list, status_code: int):
        return jsonify({
            "error": _(error),
            "details": details
        }), status_code
    def _ok(response, details: list, status_code: int):
        return jsonify({
            "response": _(response),
            "details": details
        }), status_code
    def _ok_data(response, details, status_code: int):
        return jsonify({
            "response": response,
            "details": details
            }), status_code
