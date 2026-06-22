"""MCP Tools 註冊 — 將業務工具接入 MCP 協議。"""
from __future__ import annotations

from ark_team_core import McpRegistry, ToolDefinition

from my_team.tools import TOOL_DEFINITIONS

HANDLERS: dict[str, object] = {
    # 業務工具 handler 在此註冊
    # "tool_name": handler_function,
}


def register_tools(registry: McpRegistry) -> None:
    """將業務工具註冊到 MCP Server。"""
    for defn in TOOL_DEFINITIONS:
        name = defn["name"]
        handler = HANDLERS.get(name)
        if handler:
            registry.register(ToolDefinition(
                name=name,
                description=defn["description"],
                input_schema=defn["inputSchema"],
                handler=handler,
            ))
