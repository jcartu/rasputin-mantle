from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, time, timezone
from decimal import Decimal
from typing import Any, AsyncIterator

try:
    import asyncpg
except ImportError:  # pragma: no cover - exercised only in environments missing the declared dependency.
    asyncpg = None  # type: ignore[assignment]

try:
    import psycopg2
except ImportError:  # pragma: no cover
    psycopg2 = None  # type: ignore[assignment]

from gateway.config import settings

DEFAULT_POSTGRES_DSN = "postgresql://postgres:mantle-dev@127.0.0.1:5432/postgres"

CREATE_GATEWAY_COSTS_SQL = """
CREATE TABLE IF NOT EXISTS gateway_costs(
    workspace_id TEXT NOT NULL,
    model TEXT NOT NULL,
    ts TIMESTAMP NOT NULL,
    input_tokens INT NOT NULL,
    output_tokens INT NOT NULL,
    cost_usd NUMERIC NOT NULL
)
"""


@dataclass(frozen=True)
class CostRecord:
    workspace_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    daily_total_usd: float
    max_cost_dollars: float


class CostCeilingExceeded(RuntimeError):
    def __init__(self, workspace_id: str, attempted_total_usd: float, max_cost_dollars: float) -> None:
        super().__init__(
            f"Workspace {workspace_id} would exceed daily budget: "
            f"{attempted_total_usd:.6f} > {max_cost_dollars:.6f}"
        )
        self.workspace_id = workspace_id
        self.attempted_total_usd = attempted_total_usd
        self.max_cost_dollars = max_cost_dollars


class CostWall:
    def __init__(
        self,
        *,
        dsn: str = DEFAULT_POSTGRES_DSN,
        max_cost_dollars: float | None = None,
        pool: Any | None = None,
    ) -> None:
        self.dsn = dsn
        self.max_cost_dollars = settings.max_cost_dollars if max_cost_dollars is None else max_cost_dollars
        self._pool = pool
        self._owns_pool = pool is None
        self._schema_ready = False

    async def __aenter__(self) -> CostWall:
        await self.open()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.close()

    async def open(self) -> None:
        pool = await self._get_pool()
        await self._ensure_schema(pool)

    async def close(self) -> None:
        if self._pool is not None and self._owns_pool:
            await self._pool.close()
        self._pool = None
        self._schema_ready = False

    async def check_and_record(
        self,
        workspace_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
    ) -> CostRecord:
        if not workspace_id:
            raise ValueError("workspace_id is required")
        if input_tokens < 0 or output_tokens < 0 or cost_usd < 0:
            raise ValueError("tokens and cost_usd must be non-negative")

        pool = await self._get_pool()
        await self._ensure_schema(pool)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        day_start = datetime.combine(now.date(), time.min)

        async with _acquire(pool) as conn:
            tx = conn.transaction()
            await tx.start()
            finished = False
            try:
                spent = await conn.fetchval(
                    """
                    SELECT COALESCE(SUM(cost_usd), 0)
                    FROM gateway_costs
                    WHERE workspace_id = $1 AND ts >= $2
                    """,
                    workspace_id,
                    day_start,
                )
                current_total = float(spent or Decimal("0"))
                attempted_total = current_total + float(cost_usd)
                if attempted_total > self.max_cost_dollars:
                    await tx.rollback()
                    finished = True
                    raise CostCeilingExceeded(workspace_id, attempted_total, self.max_cost_dollars)

                await conn.execute(
                    """
                    INSERT INTO gateway_costs(workspace_id, model, ts, input_tokens, output_tokens, cost_usd)
                    VALUES($1, $2, $3, $4, $5, $6)
                    """,
                    workspace_id,
                    model,
                    now,
                    int(input_tokens),
                    int(output_tokens),
                    Decimal(str(cost_usd)),
                )
                await tx.commit()
                finished = True
            except Exception:
                if not finished:
                    try:
                        await tx.rollback()
                    except Exception:
                        pass
                raise

        return CostRecord(
            workspace_id=workspace_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            daily_total_usd=attempted_total,
            max_cost_dollars=self.max_cost_dollars,
        )

    async def _get_pool(self) -> Any:
        if self._pool is None:
            if asyncpg is not None:
                self._pool = await asyncpg.create_pool(dsn=self.dsn, min_size=1, max_size=5)
            elif psycopg2 is not None:
                self._pool = _PsycopgCompatPool(self.dsn)
            else:
                raise RuntimeError("asyncpg is required for Postgres-backed cost tracking")
        return self._pool

    async def _ensure_schema(self, pool: Any) -> None:
        if self._schema_ready:
            return
        async with _acquire(pool) as conn:
            await conn.execute(CREATE_GATEWAY_COSTS_SQL)
        self._schema_ready = True


@asynccontextmanager
async def _acquire(pool: Any) -> AsyncIterator[Any]:
    acquired = pool.acquire()
    if hasattr(acquired, "__aenter__"):
        async with acquired as conn:
            yield conn
        return

    conn = await acquired
    try:
        yield conn
    finally:
        release = getattr(pool, "release", None)
        if release is not None:
            await release(conn)


default_cost_wall = CostWall()


class _PsycopgCompatTransaction:
    def __init__(self, conn: Any) -> None:
        self._conn = conn

    async def start(self) -> None:
        return None

    async def commit(self) -> None:
        self._conn.commit()

    async def rollback(self) -> None:
        self._conn.rollback()


class _PsycopgCompatConnection:
    def __init__(self, conn: Any) -> None:
        self._conn = conn

    def transaction(self) -> _PsycopgCompatTransaction:
        return _PsycopgCompatTransaction(self._conn)

    async def execute(self, query: str, *args: Any) -> None:
        with self._conn.cursor() as cursor:
            cursor.execute(_pg_placeholders(query), args or None)
        if query.lstrip().upper().startswith("CREATE TABLE"):
            self._conn.commit()

    async def fetchval(self, query: str, *args: Any) -> Any:
        with self._conn.cursor() as cursor:
            cursor.execute(_pg_placeholders(query), args or None)
            row = cursor.fetchone()
        return row[0] if row else None


class _PsycopgAcquire:
    def __init__(self, pool: _PsycopgCompatPool) -> None:
        self._pool = pool
        self._conn: _PsycopgCompatConnection | None = None

    async def __aenter__(self) -> _PsycopgCompatConnection:
        self._conn = _PsycopgCompatConnection(self._pool._connect())
        return self._conn

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._conn is not None:
            self._conn._conn.close()


class _PsycopgCompatPool:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def acquire(self) -> _PsycopgAcquire:
        return _PsycopgAcquire(self)

    async def close(self) -> None:
        return None

    def _connect(self) -> Any:
        if psycopg2 is None:
            raise RuntimeError("psycopg2 fallback is unavailable")
        return psycopg2.connect(self._dsn)


def _pg_placeholders(query: str) -> str:
    converted = query
    for index in range(1, 16):
        converted = converted.replace(f"${index}", "%s")
    return converted
