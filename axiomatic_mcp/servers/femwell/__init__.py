def main():
    """Main entry point for the Femwell server."""
    from .server import mcp

    mcp.run(transport="stdio")


