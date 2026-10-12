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

import argparse

def main():
    parser = argparse.ArgumentParser(description="ApexRev Enterprise AI Agent Platform")
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"), help="Host to bind server")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)), help="Port to listen on")
    args = parser.parse_args()
    start_server(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
