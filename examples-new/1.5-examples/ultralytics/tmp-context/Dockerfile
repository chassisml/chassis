FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install -y libgl1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file and pip install.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint file and gRPC server implementation.
COPY entrypoint.py ./

# Copy app folder.
COPY chassis chassis

# Copy the app and data
COPY data data

CMD ["python3", "entrypoint.py"]