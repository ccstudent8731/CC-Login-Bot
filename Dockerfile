FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cron \
        wget \
        gnupg \
        ca-certificates \
        fonts-noto-core \
        fonts-unifont \
        fonts-liberation \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libgtk-3-0 \
        libnss3 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libgbm1 \
        libxshmfence1 \
        libasound2 \
        libpangocairo-1.0-0 \
        libpango-1.0-0 \
        libffi8 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cron \
        wget \
        gnupg \
        ca-certificates \
        fonts-noto-core \
        fonts-unifont \
        fonts-liberation \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libgtk-3-0 \
        libnss3 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libgbm1 \
        libxshmfence1 \
        libasound2 \
        libpangocairo-1.0-0 \
        libpango-1.0-0 \
        libffi8 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./

ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]

