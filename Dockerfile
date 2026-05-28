FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Upgrade pip first
RUN pip install --upgrade pip

# Copy dependency file first for caching
COPY requirements/requirements.txt /app/requirements/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements/requirements.txt

# Copy source code
COPY . /app/

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "uvicorn src.api.rest.app:app --host 0.0.0.0 --port ${PORT}"]