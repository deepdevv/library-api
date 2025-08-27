from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class _ErrorBody(BaseModel):
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
