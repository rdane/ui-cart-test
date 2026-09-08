FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app

# Wayland/Ozone libs for native headed rendering (see scripts/run-headed.sh).
RUN apt-get update && apt-get install -y --no-install-recommends \
        libwayland-client0 libwayland-egl1 libwayland-cursor0 libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["pytest"]

