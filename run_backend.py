# run_backend.py
import subprocess
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

uvicorn_command = [
    sys.executable,
    "-m", "uvicorn",
    "api:app",
    "--host", "0.0.0.0",
    "--port", "8000"
]

print(f"Executing command: {' '.join(uvicorn_command)}")

try:
    subprocess.run(uvicorn_command, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error executing uvicorn: {e}")
    sys.exit(e.returncode)
except FileNotFoundError:
    print(f"Error: Python interpreter or uvicorn not found. "
          f"Ensure uvicorn is installed and Python is in your PATH.")
    sys.exit(1)