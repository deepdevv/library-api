from app.schemas.errors import ErrorEnvelope


def test_error_envelope_roundtrip():
    payload = {
        "error": {
            "code": "validation",
            "message": "Invalid payload.",
            "details": {"serial_number": "must be exactly six digits"},
        }
    }
    env = ErrorEnvelope.model_validate(payload)
    assert env.error.code == "validation"
    assert "serial_number" in env.error.details
    # Re-serialize
    assert ErrorEnvelope.model_validate(env.model_dump())
