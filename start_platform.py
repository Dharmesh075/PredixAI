"""
PredixAI All-in-One Platform Runner.
Launches FastAPI Backend, Vite React Frontend, and optional Telemetry Simulator.
"""

import subprocess
import time
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")


def main():
    print("=" * 65)
    print("  PREDIXAI - INTELLIGENT PREDICTIVE MAINTENANCE PLATFORM")
    print("=" * 65)

    print("\n[1/3] Starting FastAPI Prognostics Backend on http://localhost:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=BACKEND_DIR
    )

    time.sleep(3)

    print("[2/3] Starting React Industrial Dashboard on http://localhost:5173 ...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=FRONTEND_DIR
    )

    print("\n" + "-" * 65)
    print("  [ONLINE] Backend API:       http://localhost:8000")
    print("  [ONLINE] Swagger Docs:      http://localhost:8000/docs")
    print("  [ONLINE] React Dashboard:   http://localhost:5173")
    print("-" * 65)
    print("Press Ctrl+C to stop servers.\n")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n[STOPPING] Shutting down PredixAI servers...")
        backend_proc.terminate()
        frontend_proc.terminate()


if __name__ == "__main__":
    main()
