class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": {},
            }
        }


class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__("VALIDATION_ERROR", message, status_code=400)


class NotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__("NOT_FOUND", message, status_code=404)


class ProviderError(AppError):
    def __init__(self, message: str):
        super().__init__("PROVIDER_ERROR", message, status_code=502)


class StorageError(AppError):
    def __init__(self, message: str):
        super().__init__("STORAGE_ERROR", message, status_code=500)


class ParsingError(AppError):
    def __init__(self, message: str):
        super().__init__("PARSING_ERROR", message, status_code=400)


class VectorDBError(AppError):
    def __init__(self, message: str):
        super().__init__("VECTOR_DB_ERROR", message, status_code=500)
