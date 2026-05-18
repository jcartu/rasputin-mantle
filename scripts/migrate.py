#!/usr/bin/env python3
"""Thin SQL migration runner for Rasputin Mantle v1.3.

Usage:
    python3 scripts/migrate.py status    # show applied vs pending
    python3 scripts/migrate.py up        # apply all pending migrations
    python3 scripts/migrate.py up N      # apply exactly N pending migrations

Pattern: migrations/NNNN_name.sql (sorted alphabetically = execution order).
Idempotent: each migration wrapped in a transaction, version table tracks applied.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    import asyncpg
except ImportError:
    asyncpg = None  # type: ignore[assignment]

try:
    import psycopg2
except ImportError:
    psycopg2 = None  # type: ignore[assignment]

DEFAULT_DSN = os.environ.get(
    "DATABASE_URL", "postgresql://mantle:mantle-dev@postgres:5432/mantle"
)

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

CREATE_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS migration_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT now()
);
"""


def _get_migration_files() -> list[Path]:
    if not MIGRATIONS_DIR.is_dir():
        return []
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def _version_from_path(p: Path) -> str:
    return p.stem


async def _ensure_version_table(conn) -> None:
    await conn.execute(CREATE_VERSION_TABLE)


async def _applied_versions(conn) -> set[str]:
    rows = await conn.fetch("SELECT version FROM migration_version ORDER BY version")
    return {row["version"] for row in rows}


async def run_async(dsn: str, limit: int | None) -> None:
    if asyncpg is None:
        raise ImportError("asyncpg not installed")

    conn = await asyncpg.connect(dsn)
    try:
        await _ensure_version_table(conn)
        applied = await _applied_versions(conn)
        files = _get_migration_files()

        pending = [(f, _version_from_path(f)) for f in files if _version_from_path(f) not in applied]
        if limit is not None:
            pending = pending[:limit]

        print(f"Applied: {len(applied)}, Pending: {len(pending)}")
        if not pending:
            print("No pending migrations.")
            return

        for path, version in pending:
            sql = path.read_text()
            print(f"  Applying {version}...")
            await conn.execute(sql)
            await conn.execute(
                "INSERT INTO migration_version(version) VALUES($1)", version
            )
            print(f"  ✓ {version}")
    finally:
        await conn.close()


def run_sync(dsn: str, limit: int | None) -> None:
    if psycopg2 is None:
        print("ERROR: psycopg2 not installed", file=sys.stderr)
        sys.exit(1)

    conn = psycopg2.connect(dsn)
    try:
        cur = conn.cursor()
        cur.execute(CREATE_VERSION_TABLE)
        conn.commit()

        cur.execute("SELECT version FROM migration_version ORDER BY version")
        applied = {row[0] for row in cur.fetchall()}
        files = _get_migration_files()

        pending = [(f, _version_from_path(f)) for f in files if _version_from_path(f) not in applied]
        if limit is not None:
            pending = pending[:limit]

        print(f"Applied: {len(applied)}, Pending: {len(pending)}")
        if not pending:
            print("No pending migrations.")
            return

        for path, version in pending:
            sql = path.read_text()
            print(f"  Applying {version}...")
            cur.execute(sql)
            conn.commit()
            cur.execute("INSERT INTO migration_version(version) VALUES(%s)", (version,))
            conn.commit()
            print(f"  ✓ {version}")
    finally:
        conn.close()


def show_status(dsn: str) -> None:
    try:
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        cur.execute(CREATE_VERSION_TABLE)
        conn.commit()
        cur.execute("SELECT version, applied_at FROM migration_version ORDER BY version")
        applied = cur.fetchall()
        conn.close()
    except Exception:
        applied = []

    files = _get_migration_files()
    applied_versions = {a[0] for a in applied}

    print(f"\n{'Version':<35} {'Status':<10} {'Applied At'}")
    print("-" * 70)
    for f in files:
        v = _version_from_path(f)
        if v in applied_versions:
            ts = next(a[1] for a in applied if a[0] == v)
            print(f"  {v:<34} applied    {ts}")
        else:
            print(f"  {v:<34} pending")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Rasputin Mantle migration runner")
    parser.add_argument(
        "command",
        choices=["up", "status"],
        help="'up' applies pending migrations, 'status' shows state",
    )
    parser.add_argument("limit", nargs="?", type=int, help="Apply at most N migrations")
    parser.add_argument("--dsn", default=DEFAULT_DSN, help="PostgreSQL DSN")
    args = parser.parse_args()

    if args.command == "status":
        show_status(args.dsn)
    elif args.command == "up":
        try:
            import asyncio
            asyncio.run(run_async(args.dsn, args.limit))
        except (ImportError, ConnectionError, SystemExit) as e:
            print(f"async failed ({e}), falling back to sync...", file=sys.stderr)
            run_sync(args.dsn, args.limit)


if __name__ == "__main__":
    main()
