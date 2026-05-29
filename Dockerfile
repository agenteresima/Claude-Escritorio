FROM python:3.11-slim

# System deps for TA-Lib (C library)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ wget make \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library
RUN wget -q http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib && ./configure --prefix=/usr && make && make install \
    && cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directories
RUN mkdir -p data/cache models reports logs

# Default: run the live trader in dry-run mode
# Override CMD in docker-compose to run dashboard, API, etc.
CMD ["python", "main.py", "live", "--dry-run"]
