"""
Run the Better Prompt API server.

Usage:
    python run_api.py
    
Or with custom settings:
    python run_api.py --host 0.0.0.0 --port 8000 --reload
"""

import uvicorn
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Better Prompt API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              Better Prompt API Server                    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

🚀 Starting server...
📍 Host: {args.host}
🔌 Port: {args.port}
📚 Docs: http://{args.host}:{args.port}/docs
🔄 Reload: {'Enabled' if args.reload else 'Disabled'}

""")
    
    uvicorn.run(
        "better_prompt.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )
