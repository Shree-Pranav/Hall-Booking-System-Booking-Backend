FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Upgrade pip first
RUN pip install --upgrade pip

# Copy dependency file first for caching
COPY pyproject.toml /app/

# Install dependencies
RUN python - <<'PY'
import tomllib, sys, subprocess

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

deps = data.get("project", {}).get("dependencies", [])

if deps:
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-cache-dir",
        *deps
    ])
else:
    print("No dependencies found")
PY

# Copy source code
COPY . /app/

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "uvicorn src.api.rest.app:app --host 0.0.0.0 --port ${PORT}"]