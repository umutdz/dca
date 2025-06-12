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

    INVALID_CREDENTIALS = (1000, "Invalid credentials", 401, "Invalid credentials")
