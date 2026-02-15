from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel


class CaseRead(BaseModel):
    id: uuid.UUID
    invoice_id: uuid.UUID
    stage: str
    status: str
    next_action_at: dt.datetime | None = None
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = {"from_attributes": True}

