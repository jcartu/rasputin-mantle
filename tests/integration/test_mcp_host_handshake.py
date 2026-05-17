from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from mcp_host import MCPHost


@pytest.mark.asyncio
async def test_mcp_host_stdio_handshake(tmp_path: Path) -> None:
    server = tmp_path / "mock_mcp_server.py"
    server.write_text(
        """
from __future__ import annotations

import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "serverInfo": {"name": "mock", "version": "1"}, "capabilities": {"tools": {}}}
    elif method == "tools/list":
        result = {"tools": [{"name": "echo", "description": "Echo input", "inputSchema": {"type": "object"}}]}
    elif method == "tools/call":
        result = {"content": [{"type": "text", "text": request.get("params", {}).get("arguments", {}).get("text", "")}], "isError": False}
    else:
        print(json.dumps({"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32601, "message": "unknown"}}), flush=True)
        continue
    print(json.dumps({"jsonrpc": "2.0", "id": request.get("id"), "result": result}), flush=True)
""".strip()
    )

    host = MCPHost()
    try:
        init = await host.connect(f"stdio:{sys.executable} {server}")
        tools = await host.list_tools()
        call = await host.call_tool("echo", {"text": "mantle"})
    finally:
        await host.close()

    assert init["protocolVersion"] == "2024-11-05"
    assert tools[0]["name"] == "echo"
    assert call["content"][0]["text"] == "mantle"
