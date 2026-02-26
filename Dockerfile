FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies layer — only re-runs when requirement.txt changes
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Application code
COPY . .

RUN chmod +x /app/entrypoint.sh

EXPOSE 7860

# For HF Spaces (no docker-compose): download models at build time so they
# are baked into the image. docker-compose uses the named volume instead.
ARG BAKE_MODELS=false
RUN if [ "$BAKE_MODELS" = "true" ]; then python /app/download_models.py; fi

ENTRYPOINT ["/app/entrypoint.sh"]
