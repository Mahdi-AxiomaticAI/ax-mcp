def main():
    """Main entry point for the Tidy3D server."""
    from .server import mcp

    mcp.run(transport="stdio")


