FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (needed for compiling some python wheels if needed, though most have pre-built wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Default command runs the simulation
CMD ["python", "run_simulation.py"]
