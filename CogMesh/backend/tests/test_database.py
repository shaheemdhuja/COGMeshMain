"""Tests for database engine, ORM models, and BaseRepository CRUD operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.repository.base import BaseRepository
from app.models.device import Device
from app.models.goal import Goal


@pytest.mark.asyncio
async def test_goal_repository_crud(db_session: AsyncSession) -> None:
    """Test creating, reading, updating, and deleting a Goal entity."""
    repo = BaseRepository(Goal, db_session)

    # 1. Create
    goal = Goal(
        natural_language_input="Summarize lecture notes and generate MCQs",
        status="PENDING",
    )
    created_goal = await repo.create(goal)
    assert created_goal.id is not None
    assert created_goal.natural_language_input == "Summarize lecture notes and generate MCQs"

    # 2. Get by ID
    fetched_goal = await repo.get_by_id(created_goal.id)
    assert fetched_goal is not None
    assert fetched_goal.id == created_goal.id

    # 3. Update
    fetched_goal.status = "PROCESSING"
    updated_goal = await repo.update(fetched_goal)
    assert updated_goal.status == "PROCESSING"

    # 4. Delete
    await repo.delete(updated_goal)
    deleted_goal = await repo.get_by_id(created_goal.id)
    assert deleted_goal is None


@pytest.mark.asyncio
async def test_device_repository_crud(db_session: AsyncSession) -> None:
    """Test creating and listing Device entities."""
    repo = BaseRepository(Device, db_session)

    dev1 = Device(device_name="Master Laptop", device_type="LAPTOP", ip_address="192.168.1.50", port=8000, status="ONLINE")
    dev2 = Device(device_name="Phone A", device_type="PHONE", ip_address="192.168.1.51", port=8000, status="ONLINE")

    await repo.create(dev1)
    await repo.create(dev2)

    all_devices = await repo.get_all()
    assert len(all_devices) == 2
    device_names = [d.device_name for d in all_devices]
    assert "Master Laptop" in device_names
    assert "Phone A" in device_names
