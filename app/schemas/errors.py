"""Pydantic schemas for error responses.

These models standardize error envelopes returned by the API,
ensuring consistent structure for all client-visible errors.
"""

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class _ErrorBody(BaseModel):
    """Structured error payload.

    Attributes:
        code (str): Machine-readable error code.
        message (str): Human-readable explanation of the error.
        details (dict | None): Optional field-level details or extra context.
    """
    code: Literal["not_found", "conflict", "validation", "bad_request"] = Field(
        ...,
        description="Machine-readable error code.",
        examples=["conflict"],
    )
    message: str = Field(..., description="Human-readable error message.")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional field-wise validation details or context.",
    )


class ErrorEnvelope(BaseModel):
    """Top-level error response envelope.

    Wraps the structured error body under an `error` key to make
    responses consistent and predictable for clients.
    """
    error: _ErrorBody

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"error": {"code": "conflict", "message": "Book is already borrowed."}},
                {
                    "error": {
                        "code": "validation",
                        "message": "Invalid payload.",
                        "details": {"serial_number": "must be exactly six digits"},
                    }
                },
            ]
        }
    }
