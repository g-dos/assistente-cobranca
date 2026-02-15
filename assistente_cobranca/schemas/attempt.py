from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel


class AttemptRead(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    canal: str
    template_key: str | None = None
    status: str
    sent_at: dt.datetime | None = None
    error: str | None = None
    created_at: dt.datetime

    model_config = {"from_attributes": True}

