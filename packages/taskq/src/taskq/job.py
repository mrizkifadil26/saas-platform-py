from __future__ import annotations

import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field


class JobEnvelope(BaseModel):
    job_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the job",
    )
    type: str = Field(..., description="Type/category of the job")
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="The data associated with the job",
    )

    retries: int = Field(
        default=0,
        ge=0,
        description="Number of times the job has been retried",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum number of retries allowed for the job",
    )

    # priority: int = Field(0, description="Priority level of the job, higher means more urgent")  # noqa: E501
    # created_at: str = Field(..., description="Timestamp when the job was created")
    # updated_at: str = Field(..., description="Timestamp when the job was last updated")  # noqa: E501

    # Optional routing
    tube: Optional[str] = None

    def bump_attempt(self) -> JobEnvelope:
        """
        Return a copy of this envelope with retries incremented.
        """
        return self.model_copy(update={"retries": self.retries + 1})

    def should_retry(self) -> bool:
        """
        Whether the job should be retried again.
        """
        return self.retries < self.max_retries

    def to_json(self) -> str:
        return self.model_dump_json()

    @staticmethod
    def from_json(raw: str | bytes) -> JobEnvelope:
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        return JobEnvelope.model_validate_json(raw)
