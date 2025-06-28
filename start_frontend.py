#!/usr/bin/env python3
"""
Start the Morvo13 frontend server
"""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Start the frontend server"""
    frontend_dir = Path(__file__).parent / "frontend"
    server_script = frontend_dir / "server.py"

    if not server_script.exists():
        print("❌ Frontend server script not found!")
        print(f"Expected: {server_script}")
        return 1

    try:
        print("🚀 Starting Morvo13 Frontend...")
        subprocess.run([sys.executable, str(server_script)], cwd=frontend_dir)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
