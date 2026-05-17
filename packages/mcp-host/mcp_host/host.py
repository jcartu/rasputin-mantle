from __future__ import annotations

import asyncio
import json
import shlex
from dataclasses import dataclass
from typing import Any


class MCPHostError(RuntimeError):
    pass


@dataclass
class _PendingRequest:
    method: str
    params: dict[str, Any]


class MCPHost:
    def __init__(self) -> None:
        self._request_id = 0
        self._transport: str | None = None
        self._process: asyncio.subprocess.Process | None = None
        self._websocket: Any = None

    async def connect(self, server_url: str) -> dict[str, Any]:
        if server_url.startswith(("ws://", "wss://")):
            await self._connect_websocket(server_url)
        elif server_url.startswith("stdio:"):
            await self._connect_stdio(server_url[len("stdio:") :].strip())
        else:
            raise MCPHostError("server_url must start with stdio:, ws://, or wss://")

        return await self._request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "rasputin-mantle-mcp-host", "version": "0.1.0"},
            },
        )

    async def list_tools(self) -> list[dict[str, Any]]:
        result = await self._request("tools/list", {})
        tools = result.get("tools", result) if isinstance(result, dict) else result
        if not isinstance(tools, list):
            raise MCPHostError("tools/list returned an invalid payload")
        return [tool if isinstance(tool, dict) else {"name": str(tool)} for tool in tools]

    async def call_tool(self, name: str, args: dict[str, Any] | None = None) -> Any:
        if not name:
            raise ValueError("name must not be empty")
        return await self._request("tools/call", {"name": name, "arguments": args or {}})

    async def close(self) -> None:
        if self._websocket is not None:
            await self._websocket.close()
            self._websocket = None
        if self._process is not None:
            self._process.terminate()
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5)
            except TimeoutError:
                self._process.kill()
                await self._process.wait()
            self._process = None
        self._transport = None

    async def _connect_stdio(self, command: str) -> None:
        argv = shlex.split(command)
        if not argv:
            raise MCPHostError("stdio command is empty")
        self._process = await asyncio.create_subprocess_exec(
            *argv,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._transport = "stdio"

    async def _connect_websocket(self, server_url: str) -> None:
        try:
            import websockets
        except ImportError as exc:
            raise MCPHostError("websockets package is required for WebSocket MCP transport") from exc
        self._websocket = await websockets.connect(server_url)
        self._transport = "websocket"

    async def _request(self, method: str, params: dict[str, Any]) -> Any:
        self._request_id += 1
        request = {"jsonrpc": "2.0", "id": self._request_id, "method": method, "params": params}
        await self._send(request)
        response = await self._receive_matching(_PendingRequest(method=method, params=params), request["id"])
        if "error" in response:
            raise MCPHostError(f"MCP {method} failed: {response['error']}")
        return response.get("result")

    async def _send(self, request: dict[str, Any]) -> None:
        if self._transport == "stdio":
            if self._process is None or self._process.stdin is None:
                raise MCPHostError("stdio transport is not connected")
            self._process.stdin.write(json.dumps(request, separators=(",", ":")).encode() + b"\n")
            await self._process.stdin.drain()
            return
        if self._transport == "websocket":
            if self._websocket is None:
                raise MCPHostError("WebSocket transport is not connected")
            await self._websocket.send(json.dumps(request, separators=(",", ":")))
            return
        raise MCPHostError("MCP host is not connected")

    async def _receive_matching(self, pending: _PendingRequest, request_id: int) -> dict[str, Any]:
        while True:
            response = await self._receive_one()
            if response.get("id") == request_id:
                return response
            if response.get("method"):
                continue
            raise MCPHostError(f"MCP {pending.method} received mismatched response id")

    async def _receive_one(self) -> dict[str, Any]:
        if self._transport == "stdio":
            if self._process is None or self._process.stdout is None:
                raise MCPHostError("stdio transport is not connected")
            line = await self._process.stdout.readline()
            if not line:
                stderr = b""
                if self._process.stderr is not None:
                    try:
                        stderr = await asyncio.wait_for(self._process.stderr.read(), timeout=0.2)
                    except TimeoutError:
                        stderr = b""
                raise MCPHostError(f"MCP stdio server closed stdout. stderr={stderr.decode(errors='replace')[:500]}")
            return _decode_json(line)
        if self._transport == "websocket":
            if self._websocket is None:
                raise MCPHostError("WebSocket transport is not connected")
            message = await self._websocket.recv()
            if isinstance(message, bytes):
                message = message.decode()
            return _decode_json(message)
        raise MCPHostError("MCP host is not connected")


def _decode_json(payload: bytes | str) -> dict[str, Any]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise MCPHostError(f"Invalid JSON-RPC payload: {payload!r}") from exc
    if not isinstance(data, dict):
        raise MCPHostError("JSON-RPC payload must be an object")
    return data
