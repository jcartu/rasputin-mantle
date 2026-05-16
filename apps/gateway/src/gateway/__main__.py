from __future__ import annotations

import uvicorn

from gateway.config import settings


def main() -> None:
    uvicorn.run("gateway.app:app", host=settings.bind_host, port=settings.bind_port, reload=settings.debug)


if __name__ == "__main__":
    main()
