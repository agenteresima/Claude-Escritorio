FROM python:3.11-slim

# System deps (no TA-Lib needed — indicators are pure numpy/pandas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directories
RUN mkdir -p data/cache models reports logs

# Default: run the live trader in dry-run mode
# Override CMD in docker-compose to run dashboard, API, etc.
CMD ["python", "main.py", "live", "--dry-run"]
