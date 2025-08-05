#!/bin/bash

# Script d'entrada per al contenidor Docker

set -e

# Funcions d'utilitat
log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

log_warning() {
    echo "[WARNING] $1" >&2
}

# Verifica variables d'entorn obligatòries
if [ -z "$BLUETTI_MAC" ]; then
    log_error "BLUETTI_MAC no està definit"
    exit 1
fi

if [ -z "$MQTT_HOST" ]; then
    log_error "MQTT_HOST no està definit"
    exit 1
fi

# Verifica que el fitxer de claus existeixi
if [ ! -f "$ENCRYPTION_KEY_FILE" ]; then
    log_error "Fitxer de claus d'encriptació no trobat: $ENCRYPTION_KEY_FILE"
    log_error "Munta un volum amb el fitxer encryption_keys.json a /app/config/"
    exit 1
fi

# Construeix arguments de la comanda
ARGS="--broker $MQTT_HOST"

if [ -n "$MQTT_PORT" ] && [ "$MQTT_PORT" != "1883" ]; then
    ARGS="$ARGS --port $MQTT_PORT"
fi

if [ -n "$MQTT_USERNAME" ]; then
    ARGS="$ARGS --username $MQTT_USERNAME"
fi

if [ -n "$MQTT_PASSWORD" ]; then
    ARGS="$ARGS --password $MQTT_PASSWORD"
fi

if [ -n "$POLLING_INTERVAL" ]; then
    ARGS="$ARGS --interval $POLLING_INTERVAL"
fi

if [ -n "$HA_CONFIG" ]; then
    ARGS="$ARGS --ha-config $HA_CONFIG"
fi

if [ "$VERBOSE" = "true" ]; then
    ARGS="$ARGS -v"
fi

# Afegeix l'adreça MAC
ARGS="$ARGS $BLUETTI_MAC"

log_info "Iniciant Bluetti MQTT Bridge..."
log_info "MAC: $BLUETTI_MAC"
log_info "MQTT Host: $MQTT_HOST:$MQTT_PORT"
log_info "Encryption Keys: $ENCRYPTION_KEY_FILE"

# Executa la comanda segons el primer argument
case "$1" in
    bluetti-mqtt)
        log_info "Executant: python -m bluetti_mqtt.server_cli $ARGS"
        exec python -m bluetti_mqtt.server_cli $ARGS
        ;;
    bluetti-discovery)
        log_info "Executant descobriment de dispositius..."
        exec python -m bluetti_mqtt.discovery_cli --scan
        ;;
    bluetti-logger)
        if [ -z "$LOG_FILE" ]; then
            LOG_FILE="/app/logs/bluetti.log"
        fi
        log_info "Executant logger: $LOG_FILE"
        exec python -m bluetti_mqtt.logger_cli --log "$LOG_FILE" "$BLUETTI_MAC"
        ;;
    test-connection)
        log_info "Provant connexió amb el dispositiu..."
        exec python /app/tools/test_connection.py "$BLUETTI_MAC"
        ;;
    verify-keys)
        log_info "Verificant claus d'encriptació..."
        exec python /app/tools/verify_keys.py "$BLUETTI_MAC"
        ;;
    bash|sh)
        log_info "Iniciant shell interactiu..."
        exec "$@"
        ;;
    *)
        log_info "Executant comanda personalitzada: $@"
        exec "$@"
        ;;
esac