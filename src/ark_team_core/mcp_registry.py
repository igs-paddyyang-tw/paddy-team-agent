from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class ToolDefinition:
    name: str
    description: str
    handler: Callable | None = None
    parameters: dict = field(default_factory=dict)

class McpRegistry:
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, name: str, description: str, handler: Callable | None = None, parameters: dict | None = None) -> None:
        self._tools[name] = ToolDefinition(name=name, description=description, handler=handler, parameters=parameters or {})

    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())
