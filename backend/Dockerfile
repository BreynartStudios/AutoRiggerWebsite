FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies + Blender from Ubuntu repos (works on ARM64)
RUN apt-get update && apt-get install -y \
    blender \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY blender_scripts/ ./blender_scripts/

RUN mkdir -p /app/data/uploads \
    /app/data/processed \
    /app/data/animations/locomotion \
    /app/data/animations/combat \
    /app/data/animations/social \
    /app/data/animations/misc \
    /app/data/exports \
    /app/data/templates

COPY data/animations/ /app/data/animations/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
