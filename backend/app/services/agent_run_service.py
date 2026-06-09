"""Agent run service — DB operations for AgentRun and AgentSchedule."""

import math
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import AgentRun, AgentSchedule
from app.schemas.agent import AgentScheduleUpdate


async def list_agent_runs(
    db: AsyncSession,
    owner_id: uuid.UUID,
    *,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[AgentRun], int]:
    """Return paginated AgentRun records for the owner, newest first."""
    count_q = select(func.count()).select_from(AgentRun).where(
        AgentRun.owner_id == owner_id
    )
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * limit
    stmt = (
        select(AgentRun)
        .where(AgentRun.owner_id == owner_id)
        .order_by(AgentRun.started_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = (await db.execute(stmt)).scalars().all()
    return list(rows), total


async def get_agent_run(
    db: AsyncSession,
    run_id: uuid.UUID,
    owner_id: uuid.UUID,
) -> AgentRun | None:
    """Fetch a single AgentRun by ID, scoped to the owner."""
    result = await db.execute(
        select(AgentRun).where(
            AgentRun.id == run_id,
            AgentRun.owner_id == owner_id,
        )
    )
    return result.scalar_one_or_none()


async def get_agent_schedule(
    db: AsyncSession,
    owner_id: uuid.UUID,
) -> AgentSchedule | None:
    """Fetch the AgentSchedule for the owner, or None if not configured."""
    result = await db.execute(
        select(AgentSchedule).where(AgentSchedule.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def upsert_agent_schedule(
    db: AsyncSession,
    owner_id: uuid.UUID,
    data: AgentScheduleUpdate,
) -> AgentSchedule:
    """Create or update the AgentSchedule for the owner."""
    result = await db.execute(
        select(AgentSchedule).where(AgentSchedule.owner_id == owner_id)
    )
    schedule = result.scalar_one_or_none()

    if schedule is None:
        schedule = AgentSchedule(
            owner_id=owner_id,
            cron_expr=data.cron_expr,
            is_active=data.is_active,
        )
        db.add(schedule)
    else:
        schedule.cron_expr = data.cron_expr
        schedule.is_active = data.is_active

    await db.flush()
    await db.refresh(schedule)
    return schedule
