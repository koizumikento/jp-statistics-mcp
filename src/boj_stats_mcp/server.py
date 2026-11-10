from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from .client import (
    get_multiple_series_data,
    get_series_data,
    get_series_data_by_layer,
    search_series,
)

READ_ONLY = ToolAnnotations(
    read_only_hint=True, idempotent_hint=True, destructive_hint=False, open_world_hint=True
)


def create_server() -> MCPServer:
    mcp = MCPServer("boj-stats-mcp")
    mcp.tool(annotations=READ_ONLY)(search_series)
    mcp.tool(annotations=READ_ONLY)(get_series_data)
    mcp.tool(annotations=READ_ONLY)(get_multiple_series_data)
    mcp.tool(annotations=READ_ONLY)(get_series_data_by_layer)
    return mcp
