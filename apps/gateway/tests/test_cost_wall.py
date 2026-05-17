from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from gateway.cost_wall import CostCeilingExceeded, CostWall


class FakeTransaction:
    def __init__(self) -> None:
        self.started = False
        self.committed = False
        self.rolled_back = False

    async def start(self) -> None:
        self.started = True

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeConnection:
    def __init__(self, pool: FakePool) -> None:
        self.pool = pool
        self.last_transaction = FakeTransaction()

    def transaction(self) -> FakeTransaction:
        self.last_transaction = FakeTransaction()
        self.pool.transactions.append(self.last_transaction)
        return self.last_transaction

    async def execute(self, query: str, *args: Any) -> None:
        self.pool.executed.append((query, args))
        if query.lstrip().upper().startswith("INSERT"):
            self.pool.rows.append(
                {
                    "workspace_id": args[0],
                    "model": args[1],
                    "cost_usd": Decimal(args[5]),
                }
            )

    async def fetchval(self, query: str, *args: Any) -> Decimal:
        workspace_id = args[0]
        return sum((row["cost_usd"] for row in self.pool.rows if row["workspace_id"] == workspace_id), Decimal("0"))


class FakeAcquire:
    def __init__(self, pool: FakePool) -> None:
        self.pool = pool

    async def __aenter__(self) -> FakeConnection:
        return FakeConnection(self.pool)

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


class FakePool:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.executed: list[tuple[str, tuple[Any, ...]]] = []
        self.transactions: list[FakeTransaction] = []
        self.closed = False

    def acquire(self) -> FakeAcquire:
        return FakeAcquire(self)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_check_and_record_creates_table_and_inserts_under_budget() -> None:
    pool = FakePool()
    wall = CostWall(pool=pool, max_cost_dollars=1.0)

    record = await wall.check_and_record("workspace-a", "claude-3-5-sonnet", 10, 20, 0.25)

    assert record.workspace_id == "workspace-a"
    assert record.daily_total_usd == 0.25
    assert len(pool.rows) == 1
    assert any("CREATE TABLE IF NOT EXISTS gateway_costs" in query for query, _args in pool.executed)
    assert pool.transactions[-1].committed is True


@pytest.mark.asyncio
async def test_check_and_record_accumulates_per_workspace_daily_cost() -> None:
    pool = FakePool()
    wall = CostWall(pool=pool, max_cost_dollars=1.0)

    first = await wall.check_and_record("workspace-a", "claude-3-5-sonnet", 10, 20, 0.25)
    second = await wall.check_and_record("workspace-a", "claude-3-5-sonnet", 10, 20, 0.50)

    assert first.daily_total_usd == 0.25
    assert second.daily_total_usd == 0.75
    assert len(pool.rows) == 2


@pytest.mark.asyncio
async def test_check_and_record_isolated_by_workspace() -> None:
    pool = FakePool()
    wall = CostWall(pool=pool, max_cost_dollars=1.0)

    await wall.check_and_record("workspace-a", "claude-3-5-sonnet", 10, 20, 0.90)
    record = await wall.check_and_record("workspace-b", "claude-3-5-sonnet", 10, 20, 0.90)

    assert record.daily_total_usd == 0.90
    assert len(pool.rows) == 2


@pytest.mark.asyncio
async def test_check_and_record_raises_and_does_not_insert_when_budget_exceeded() -> None:
    pool = FakePool()
    wall = CostWall(pool=pool, max_cost_dollars=1.0)

    await wall.check_and_record("workspace-a", "claude-3-5-sonnet", 10, 20, 0.90)
    with pytest.raises(CostCeilingExceeded) as exc_info:
        await wall.check_and_record("workspace-a", "claude-3-5-sonnet", 10, 20, 0.20)

    assert exc_info.value.attempted_total_usd == pytest.approx(1.10)
    assert len(pool.rows) == 1
    assert pool.transactions[-1].rolled_back is True


@pytest.mark.asyncio
async def test_check_and_record_rejects_invalid_inputs() -> None:
    wall = CostWall(pool=FakePool(), max_cost_dollars=1.0)

    with pytest.raises(ValueError, match="workspace_id"):
        await wall.check_and_record("", "model", 0, 0, 0.0)
    with pytest.raises(ValueError, match="non-negative"):
        await wall.check_and_record("workspace-a", "model", -1, 0, 0.0)


@pytest.mark.asyncio
async def test_close_closes_owned_pool() -> None:
    pool = FakePool()
    wall = CostWall(pool=pool, max_cost_dollars=1.0)
    wall._owns_pool = True

    await wall.close()

    assert pool.closed is True
