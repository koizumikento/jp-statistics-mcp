from mcp.server import MCPServer

from boj_stats_mcp import server as boj_server
from e_stat_dashboard_mcp import server as dashboard_server


def create_server() -> MCPServer:
    mcp = MCPServer("jp-statistics-mcp")
    mcp.tool(annotations=dashboard_server.READ_ONLY)(dashboard_server.search_indicators)
    mcp.tool(annotations=dashboard_server.READ_ONLY)(dashboard_server.get_indicator_data)
    mcp.tool(annotations=dashboard_server.READ_ONLY)(dashboard_server.search_regions)
    mcp.tool(annotations=dashboard_server.READ_ONLY)(dashboard_server.search_terms)
    mcp.tool(annotations=dashboard_server.READ_ONLY)(dashboard_server.search_social_events)
    mcp.tool(annotations=dashboard_server.READ_ONLY)(dashboard_server.search_surveys)
    mcp.tool(annotations=boj_server.READ_ONLY)(boj_server.search_series)
    mcp.tool(annotations=boj_server.READ_ONLY)(boj_server.get_series_data)
    mcp.tool(annotations=boj_server.READ_ONLY)(boj_server.get_multiple_series_data)
    mcp.tool(annotations=boj_server.READ_ONLY)(boj_server.get_series_data_by_layer)
    return mcp
