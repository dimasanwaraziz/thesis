FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the unit tests first, then the full simulation
CMD ["sh", "-c", "python test_kingsley.py && python run_simulation.py"]
