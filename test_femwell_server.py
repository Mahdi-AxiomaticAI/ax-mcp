"""Test script to verify Femwell MCP server tools are registered."""

from axiomatic_mcp.servers.femwell.server import mcp

def test_server_tools():
    """Test that all Femwell tools are registered."""
    print("Testing Femwell MCP Server...")
    print(f"Server name: {mcp.name}")

    # Get list of registered tools (direct access since list_tools is async)
    tools = list(mcp._tool_manager._tools.values())
    print(f"\nNumber of tools registered: {len(tools)}")

    expected_tools = [
        "simulate_depletion_modulator",
        "simulate_metal_heater_phase_shifter",
        "simulate_doped_si_heater_phase_shifter",
        "simulate_waveguide_dispersion"
    ]

    print("\nExpected tools:")
    for tool_name in expected_tools:
        found = any(tool.name == tool_name for tool in tools)
        status = "[OK]" if found else "[MISSING]"
        print(f"  {status} {tool_name}")

    print("\nAll registered tools:")
    for tool in tools:
        print(f"  - {tool.name}")

    # Check if all expected tools are present
    all_found = all(any(tool.name == name for tool in tools) for name in expected_tools)

    if all_found:
        print("\n[SUCCESS] All 4 Femwell MCP tools are registered!")
        return True
    else:
        print("\n[ERROR] Some tools are missing!")
        return False

if __name__ == "__main__":
    success = test_server_tools()
    exit(0 if success else 1)