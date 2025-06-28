#!/usr/bin/env python3
"""
Simple HTTP server to serve the Morvo13 frontend
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path
from typing import Any

# Get the directory where this script is located
FRONTEND_DIR = Path(__file__).parent
PORT = 3001


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def end_headers(self) -> None:
        # Add CORS headers to allow communication with FastAPI backend
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()


def start_server() -> None:
    """Start the frontend server"""
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print("🚀 Morvo13 Frontend Server starting...")
            print(f"📍 Server running at: http://localhost:{PORT}")
            print(f"📁 Serving files from: {FRONTEND_DIR}")
            print("🔗 FastAPI Backend: http://localhost:8000")
            print("\n✨ Opening browser automatically...")
            print("💡 Press Ctrl+C to stop the server\n")

            # Open browser automatically
            webbrowser.open(f"http://localhost:{PORT}")

            # Start serving
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use!")
            print(f"💡 Try a different port or kill the process using port {PORT}")
        else:
            print(f"❌ Error starting server: {e}")


if __name__ == "__main__":
    start_server()
 