"""Single-command local runner for The Lenny Growth Assistant."""

import sys
from pathlib import Path
import uvicorn

# Add backend directory to Python path
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    print("=" * 70)
    print("Launching 'The Lenny Growth Assistant' on http://localhost:8000")
    print("=" * 70)
    print("• API Docs:         http://localhost:8000/docs")
    print("• Health Check:     http://localhost:8000/api/health")
    print("• Web Application:  http://localhost:8000/")
    print("-" * 70)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
