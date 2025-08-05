# Execució amb Docker

Aquest document explica com executar Bluetti Elite 200 V2 MQTT Bridge utilitzant Docker.

## Requisits

- Docker i Docker Compose instal·lats
- Adaptador Bluetooth accessible des del contenidor
- Fitxer `encryption_keys.json` amb les claus del dispositiu

## Configuració ràpida

### Opció A: Imatge pre-construïda (Recomanat)

Utilitza la imatge oficial des de GitHub Container Registry:

```bash
# Crea directoris necessaris
mkdir -p config logs

# Copia el fitxer de claus (substitueix per les teves dades reals)
cp encryption_keys.json config/

# Utilitza el docker-compose per a imatge pre-construïda
docker-compose -f docker-compose.prebuilt.yml up -d

# Veure logs
docker-compose -f docker-compose.prebuilt.yml logs -f

# Parar l'aplicació
docker-compose -f docker-compose.prebuilt.yml down
```

### Opció B: Construcció local

Construeix la imatge localment des del codi font:

```bash
# Crea directoris necessaris
mkdir -p config logs

# Copia el fitxer de claus
cp encryption_keys.json config/

# Construeix i executa localment
docker-compose up -d

# Veure logs
docker-compose logs -f

# Parar l'aplicació
docker-compose down
```

### Configuració de variables d'entorn

Edita el fitxer docker-compose corresponent i substitueix:

```yaml
environment:
  - BLUETTI_MAC=E4:B3:23:5B:F5:76    # La teva adreça MAC real
  - MQTT_HOST=192.168.1.100          # La teva IP MQTT real
  - MQTT_USERNAME=el_teu_usuari      # Si cal autenticació
  - MQTT_PASSWORD=la_teva_contrasenya # Si cal autenticació
```

## Ús avançat

### Descobriment de dispositius

```bash
# Amb imatge pre-construïda
docker-compose -f docker-compose.prebuilt.yml --profile discovery up bluetti-discovery

# Amb construcció local
docker-compose --profile discovery up bluetti-discovery

# O directament amb Docker (imatge pre-construïda)
docker run --rm --privileged --network host \
  -v /var/run/dbus:/var/run/dbus:ro \
  --device /dev/bus/usb:/dev/bus/usb \
  ghcr.io/jordigrasvi/bluetti-elite200v2-mqtt:latest bluetti-discovery
```

### Mode logger

```bash
# Amb imatge pre-construïda
docker-compose -f docker-compose.prebuilt.yml --profile logger up bluetti-logger

# Amb construcció local
docker-compose --profile logger up bluetti-logger
```

### Test de connexió

```bash
# Amb imatge pre-construïda
docker run --rm --privileged --network host \
  -v /var/run/dbus:/var/run/dbus:ro \
  --device /dev/bus/usb:/dev/bus/usb \
  -e BLUETTI_MAC=XX:XX:XX:XX:XX:XX \
  ghcr.io/jordigrasvi/bluetti-elite200v2-mqtt:latest test-connection

# Amb imatge local
docker run --rm --privileged --network host \
  -v /var/run/dbus:/var/run/dbus:ro \
  --device /dev/bus/usb:/dev/bus/usb \
  -e BLUETTI_MAC=XX:XX:XX:XX:XX:XX \
  bluetti-elite200v2-mqtt test-connection
```

### Verificació de claus

```bash
# Amb imatge pre-construïda
docker run --rm --privileged --network host \
  -v ./config:/app/config:ro \
  -v /var/run/dbus:/var/run/dbus:ro \
  --device /dev/bus/usb:/dev/bus/usb \
  -e BLUETTI_MAC=XX:XX:XX:XX:XX:XX \
  ghcr.io/jordigrasvi/bluetti-elite200v2-mqtt:latest verify-keys

# Amb imatge local
docker run --rm --privileged --network host \
  -v ./config:/app/config:ro \
  -v /var/run/dbus:/var/run/dbus:ro \
  --device /dev/bus/usb:/dev/bus/usb \
  -e BLUETTI_MAC=XX:XX:XX:XX:XX:XX \
  bluetti-elite200v2-mqtt verify-keys
```

## Variables d'entorn disponibles

| Variable | Descripció | Per defecte | Obligatori |
|----------|------------|-------------|------------|
| `BLUETTI_MAC` | Adreça MAC del dispositiu | - | ✅ |
| `MQTT_HOST` | Host del broker MQTT | - | ✅ |
| `MQTT_PORT` | Port del broker MQTT | 1883 | ❌ |
| `MQTT_USERNAME` | Usuari MQTT | - | ❌ |
| `MQTT_PASSWORD` | Contrasenya MQTT | - | ❌ |
| `MQTT_TOPIC` | Topic base MQTT | bluetti | ❌ |
| `LOG_LEVEL` | Nivell de logging | info | ❌ |
| `POLLING_INTERVAL` | Interval de polling (segons) | 5 | ❌ |
| `HA_CONFIG` | Configuració Home Assistant | normal | ❌ |
| `VERBOSE` | Logs detallats | false | ❌ |
| `ENCRYPTION_KEY_FILE` | Ruta al fitxer de claus | /app/config/encryption_keys.json | ❌ |

## Volums

| Volum local | Volum contenidor | Descripció |
|-------------|------------------|------------|
| `./config` | `/app/config` | Fitxers de configuració (encryption_keys.json) |
| `./logs` | `/app/logs` | Logs de l'aplicació |

## Resolució de problemes

### Error: "No such device"

```bash
# Verifica que l'adaptador Bluetooth sigui accessible
ls -la /dev/bus/usb/

# Assegura't que el contenidor tingui privilegis
# privileged: true al docker-compose.yml
```

### Error: "Permission denied" per Bluetooth

```bash
# Afegeix l'usuari al grup bluetooth (host)
sudo usermod -a -G bluetooth $USER

# Reinicia el servei Docker
sudo systemctl restart docker
```

### Error: "Device not found"

```bash
# Verifica que el dispositiu sigui visible
docker run --rm --privileged --network host \
  -v /var/run/dbus:/var/run/dbus:ro \
  --device /dev/bus/usb:/dev/bus/usb \
  bluetti-elite200v2-mqtt bluetti-discovery
```

### Logs detallats

```bash
# Activa logs detallats
docker-compose exec bluetti-mqtt \
  python -m bluetti_mqtt.server_cli --broker $MQTT_HOST -v $BLUETTI_MAC
```

## Construcció personalitzada

```bash
# Construeix la imatge localment
docker build -t bluetti-elite200v2-mqtt .

# Amb arguments de construcció
docker build --build-arg PYTHON_VERSION=3.11 -t bluetti-elite200v2-mqtt .
```

## Integració amb altres serveis

### Amb Home Assistant (Docker)

```yaml
# Afegeix al teu docker-compose.yml de Home Assistant
services:
  homeassistant:
    # ... configuració existent
    
  mosquitto:
    # ... configuració MQTT
    
  bluetti-mqtt:
    image: bluetti-elite200v2-mqtt
    depends_on:
      - mosquitto
    environment:
      - MQTT_HOST=mosquitto
    # ... resta de configuració
```

### Amb Portainer

1. Importa el `docker-compose.yml` a Portainer
2. Configura les variables d'entorn a la interfície web
3. Munta els volums necessaris
4. Executa el stack

## Seguretat

- **Mai** incloguis claus reals als fitxers de configuració del repositori
- Utilitza secrets de Docker per a dades sensibles en producció
- Limita l'accés als volums de configuració
- Considera utilitzar un usuari no-root dins del contenidor (ja configurat)