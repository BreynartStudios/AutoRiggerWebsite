FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV BLENDER_VERSION=4.0.2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    xz-utils \
    libxi6 \
    libxxf86vm1 \
    libxfixes3 \
    libxrender1 \
    libgl1-mesa-glx \
    libglu1-mesa \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Download and install Blender
# Adjust URL for your architecture (amd64 or arm64)
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "arm64" ]; then \
        BLENDER_ARCH="linux-arm64"; \
    else \
        BLENDER_ARCH="linux-x64"; \
    fi && \
    wget -q https://download.blender.org/release/Blender4.0/blender-${BLENDER_VERSION}-${BLENDER_ARCH}.tar.xz && \
    tar -xf blender-${BLENDER_VERSION}-${BLENDER_ARCH}.tar.xz && \
    mv blender-${BLENDER_VERSION}-${BLENDER_ARCH} /opt/blender && \
    rm blender-${BLENDER_VERSION}-${BLENDER_ARCH}.tar.xz && \
    ln -s /opt/blender/blender /usr/local/bin/blender

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
