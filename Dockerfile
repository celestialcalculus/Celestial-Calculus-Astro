FROM python:3.12-slim

WORKDIR /app

# Build tools required by pyswisseph when a prebuilt wheel
# is not available for the selected Python/platform.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       g++ \
       make \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8765

CMD ["python", "-m", "app.server", "--host", "0.0.0.0"]
