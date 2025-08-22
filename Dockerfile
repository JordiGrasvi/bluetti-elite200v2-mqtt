# Dockerfile per a Bluetti Elite 200 V2 MQTT Bridge

FROM python:3.11-slim

# Metadades
LABEL maintainer="Bluetti Elite 200 V2 Community"
LABEL description="MQTT bridge for Bluetti Elite 200 V2 power station"
LABEL version="1.0.0"

# Variables d'entorn
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Instal·la dependències del sistema
RUN apt-get update && apt-get install -y \
    bluetooth \
    bluez \
    libbluetooth-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Crea usuari no-root
RUN groupadd -r bluetti && useradd -r -g bluetti bluetti

# Directori de treball
WORKDIR /app

# Copia fitxers de dependències
COPY requirements.txt .

# Instal·la dependències Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia codi de l'aplicació
COPY bluetti_mqtt/ ./bluetti_mqtt/
COPY tools/ ./tools/
COPY setup.py pyproject.toml ./
COPY README.md ./

# Instal·la l'aplicació
RUN pip install -e .

# Crea directoris per a configuració
RUN mkdir -p /app/config /app/logs

# Canvia propietari dels fitxers
RUN chown -R bluetti:bluetti /app

# Canvia a usuari no-root
USER bluetti

# Volums per a configuració i logs
VOLUME ["/app/config", "/app/logs"]

# Port per defecte (no utilitzat directament, però informatiu)
EXPOSE 1883

# Variables d'entorn per defecte
ENV BLUETTI_MAC=""
ENV MQTT_HOST=""
ENV MQTT_PORT=1883
ENV MQTT_USERNAME=""
ENV MQTT_PASSWORD=""
ENV MQTT_TOPIC="bluetti"
ENV LOG_LEVEL="info"
ENV ENCRYPTION_KEY_FILE="/app/config/encryption_keys.json"

# Script d'entrada
COPY docker-entrypoint.sh /app/
USER root
RUN chmod +x /app/docker-entrypoint.sh
USER bluetti

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["bluetti-mqtt"]