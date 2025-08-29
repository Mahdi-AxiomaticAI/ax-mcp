def main():
    """Main entry point for the DTS server."""
    from .server import mcp

    mcp.run(transport="stdio")