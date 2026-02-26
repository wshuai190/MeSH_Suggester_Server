#!/bin/sh
# Download models into the named volume on first start; skip on subsequent starts.
if [ ! -f /app/server/Model/checkpoint-80000/pytorch_model.bin ]; then
    echo "==> Models not found — downloading (this only happens once)..."
    python /app/download_models.py
else
    echo "==> Models already present, skipping download."
fi

exec python /app/app.py "$@"
