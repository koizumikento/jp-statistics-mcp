from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from .client import (
    get_indicator_data,
    search_indicators,
    search_regions,
    search_social_events,
    search_surveys,
    search_terms,
)

READ_ONLY = ToolAnnotations(
    read_only_hint=True, idempotent_hint=True, destructive_hint=False, open_world_hint=True
)


def create_server() -> MCPServer:
    mcp = MCPServer("e-stat-dashboard-mcp")
    mcp.tool(annotations=READ_ONLY)(search_indicators)
    mcp.tool(annotations=READ_ONLY)(get_indicator_data)
    mcp.tool(annotations=READ_ONLY)(search_regions)
    mcp.tool(annotations=READ_ONLY)(search_terms)
    mcp.tool(annotations=READ_ONLY)(search_social_events)
    mcp.tool(annotations=READ_ONLY)(search_surveys)
    return mcp
