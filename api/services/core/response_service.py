from flask import jsonify
from flask_babel import _
# Setup logging
from services.logs.logger_service import setup_logger

class Response:
    @staticmethod
    def _error(error: str, details: list, status_code: int, name: str = None):
        logger = setup_logger(name or "default_error_source")  # Use a default if name is None
        logger.error(f"Error: {error}, Details: {details}")
        # Extract only the 'msg' from each error in details
        if isinstance(details, list):
            details = "\n".join([detail['msg'] for detail in details if 'msg' in detail])
        return jsonify({
            "response": error,
            "details": details
        }), status_code

    @staticmethod
    def _ok(response, details: str, status_code: int, name: str = None):
        logger = setup_logger(name or "default_ok_source")  # Use a default if name is None
        logger.info(f"Response: {_(details)}")
        return jsonify({
            "response": response,
            "details": details
        }), status_code

    @staticmethod
    def _ok_data(response:str, details:str, status_code: int, name: str = None):
        logger = setup_logger(name or "default_data_source")  # Use a default if name is None
        logger.info(f"Response: {_(details)}")
        return jsonify({
            "response": response,
            "details": details
        }), status_code
