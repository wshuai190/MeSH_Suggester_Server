FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies — cached unless requirement.txt changes
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Application code
COPY . .

RUN chmod +x /app/entrypoint.sh

# Bake models into the image.
# This layer is cached by Docker, so code-only changes don't re-download.
RUN python /app/download_models.py

EXPOSE 7860

ENTRYPOINT ["/app/entrypoint.sh"]
