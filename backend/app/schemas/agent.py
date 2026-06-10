"""Schemas for agent-related API endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# AgentRun schemas
# ---------------------------------------------------------------------------


class AgentRunResponse(BaseModel):
    """Full AgentRun record returned to the admin client."""

    id: uuid.UUID
    owner_id: uuid.UUID
    topic: str | None
    model_used: str | None
    status: str
    output_post_id: uuid.UUID | None
    run_log: dict | None
    triggered_by: str
    started_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class AgentRunListItem(BaseModel):
    """Lightweight AgentRun for list/log views (no full run_log)."""

    id: uuid.UUID
    topic: str | None
    status: str
    triggered_by: str
    output_post_id: uuid.UUID | None
    started_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# AgentSchedule schemas
# ---------------------------------------------------------------------------


class AgentScheduleResponse(BaseModel):
    """AgentSchedule record returned to the admin client."""

    id: uuid.UUID
    owner_id: uuid.UUID
    cron_expr: str
    is_active: bool
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentScheduleUpdate(BaseModel):
    """Request body for updating the agent schedule."""

    cron_expr: str = Field(
        default="0 9 * * 1",
        description="Cron expression, e.g. '0 9 * * 1' for Monday 9am.",
    )
    is_active: bool = True


# ---------------------------------------------------------------------------
# Pipeline trigger schema
# ---------------------------------------------------------------------------


class AgentTriggerResponse(BaseModel):
    """Returned immediately when the pipeline is triggered manually.

    The run is async — the client polls GET /admin/agent/runs/{run_id}
    to track progress.
    """

    run_id: uuid.UUID
    status: str = "running"
    message: str = "Pipeline started. Poll /admin/agent/runs/{run_id} for status."
