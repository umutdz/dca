from enum import IntEnum


class ErrorCode(IntEnum):
    def __new__(cls, code, message, status_code, description):
        obj = int.__new__(cls, code)
        obj._value_ = code

        obj.code = code
        obj.message = message.upper()
        obj.status_code = status_code
        obj.description = description
        return obj

    def to_dict(self):
        return {
            "error_code": self.code,
            "message": self.message,
            "status_code": self.status_code,
            "description": self.description,
        }

    @classmethod
    def get_error_by_code(cls, code):
        for error in cls:
            if error.code == code:
                return error
        return cls.UNKNOWN_API_ERROR

    def __str__(self):
        return (
            f"Error Code: {self.code}, "
            f"Message: {self.message}, "
            f"HTTP Status Code: {self.status_code}, "
            f"Description: {self.description}"
        )

    # Authentication Errors (1000-1999)
    INVALID_CREDENTIALS = (1000, "Invalid credentials", 401, "Invalid credentials")
    USER_ALREADY_EXISTS = (1001, "User already exists", 400, "User already exists")
    TOKEN_EXPIRED = (1002, "Token expired", 401, "Authentication token has expired")
    INVALID_TOKEN = (1003, "Invalid token", 401, "Invalid authentication token")
    UNAUTHORIZED_ACCESS = (1004, "Unauthorized access", 403, "User does not have permission to access this resource")

    # Validation Errors (2000-2999)
    INVALID_INPUT = (2000, "Invalid input", 400, "The provided input is invalid")
    MISSING_REQUIRED_FIELD = (2001, "Missing required field", 400, "A required field is missing")
    INVALID_FILE_TYPE = (2002, "Invalid file type", 400, "The uploaded file type is not supported")
    FILE_TOO_LARGE = (2003, "File too large", 400, "The uploaded file exceeds the maximum allowed size")

    # PDF Processing Errors (3000-3999)
    PDF_UPLOAD_FAILED = (3000, "PDF upload failed", 500, "Failed to upload PDF file")
    PDF_NOT_FOUND = (3001, "PDF not found", 404, "The requested PDF file was not found")
    PDF_PARSE_FAILED = (3002, "PDF parse failed", 500, "Failed to parse PDF file")
    PDF_ACCESS_DENIED = (3003, "PDF access denied", 403, "User does not have access to this PDF")
    PDF_ALREADY_PARSED = (3004, "PDF already parsed", 400, "PDF has already been parsed")
    PDF_SELECTION_FAILED = (3005, "PDF selection failed", 500, "Failed to select PDF for chat")

    # Database Errors (4000-4999)
    DATABASE_ERROR = (4000, "Database error", 500, "An error occurred while accessing the database")
    RECORD_NOT_FOUND = (4001, "Record not found", 404, "The requested record was not found")
    DUPLICATE_RECORD = (4002, "Duplicate record", 400, "A record with this information already exists")

    # Server Errors (5000-5999)
    INTERNAL_SERVER_ERROR = (5000, "Internal server error", 500, "An unexpected error occurred")
    SERVICE_UNAVAILABLE = (5001, "Service unavailable", 503, "The service is temporarily unavailable")
    UNKNOWN_API_ERROR = (5002, "Unknown API error", 500, "An unknown error occurred")

    # API Errors (6000-6999)
    API_ERROR = (6000, "API error", 500, "An error occurred while accessing the API")
