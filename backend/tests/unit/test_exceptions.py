from app.exceptions import (
    AppError,
    NotFoundError,
    ProviderError,
    StorageError,
    ValidationError,
)


def test_app_error_to_dict():
    """AppError produces correct JSON shape."""
    err = AppError("CODE", "msg", 500)
    assert err.to_dict() == {"error": {"code": "CODE", "message": "msg", "details": {}}}
    assert err.status_code == 500


def test_validation_error():
    """ValidationError has status_code 400."""
    err = ValidationError("bad input")
    assert err.status_code == 400
    assert err.code == "VALIDATION_ERROR"
    assert err.to_dict()["error"]["code"] == "VALIDATION_ERROR"


def test_not_found_error():
    """NotFoundError has status_code 404."""
    err = NotFoundError("missing")
    assert err.status_code == 404
    assert err.code == "NOT_FOUND"


def test_provider_error():
    """ProviderError has status_code 502."""
    err = ProviderError("upstream")
    assert err.status_code == 502
    assert err.code == "PROVIDER_ERROR"


def test_storage_error():
    """StorageError has status_code 500."""
    err = StorageError("db failure")
    assert err.status_code == 500
    assert err.code == "STORAGE_ERROR"
