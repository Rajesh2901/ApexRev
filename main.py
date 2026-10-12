"""
Entrypoint for the ApexRev Enterprise AI Agent Platform.
Usage:
    uv run python main.py
"""

import sys
import os

# Add src to sys.path so modules resolve cleanly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from apexrev.server import start_server

def main():
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    start_server(host=host, port=port)

if __name__ == "__main__":
    main()
