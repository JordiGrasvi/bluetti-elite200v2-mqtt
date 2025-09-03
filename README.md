# Bluetti Elite 200 V2 MQTT Bridge

[![CI](https://github.com/JordiGrasvi/bluetti-elite200v2-mqtt/workflows/CI/badge.svg)](https://github.com/JordiGrasvi/bluetti-elite200v2-mqtt/actions)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-blue)](https://github.com/JordiGrasvi/bluetti-elite200v2-mqtt/pkgs/container/bluetti-elite200v2-mqtt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Aquest projecte proporciona una interfície MQTT per a l'estació de càrrega Bluetti Elite 200 V2, permetent llegir dades del dispositiu via Bluetooth i publicar-les a un broker MQTT per a la seva integració amb sistemes de domòtica com Home Assistant.

## Agraïments

Aquest repositori s'ha creat gràcies al treball excepcional de [warhammerkid](https://github.com/warhammerkid) i el seu projecte [bluetti_mqtt](https://github.com/warhammerkid/bluetti_mqtt). Li agraeixo molt la seva feina, que ha fet possible aquesta adaptació específica per a la Bluetti Elite 200 V2. El codi original ha servit com a base sòlida per desenvolupar aquesta versió especialitzada.

## Característiques

- ✅ Connexió Bluetooth amb l'estació Bluetti Elite 200 V2
- ✅ Publicació de dades a MQTT
- ✅ Suport per a encriptació Bluetooth
- ✅ Integració automàtica amb Home Assistant
- ✅ Monitorització contínua de l'estat del dispositiu
- ✅ Suport per a múltiples dispositius simultàniament

## Requisits

- Python 3.7 o superior
- Adaptador Bluetooth compatible amb BLE
- Broker MQTT (com Mosquitto)
- Estació de càrrega Bluetti Elite 200 V2

## Instal·lació

### 1. Clona el repositori

```bash
git clone https://github.com/JordiGrasvi/bluetti-elite200v2-mqtt.git
cd bluetti-elite200v2-mqtt
```

### 2. Crea un entorn virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 3. Instal·la les dependències

```bash
pip install -r requirements.txt
```

### 4. Configura l'aplicació

Copia el fitxer d'exemple de configuració:

```bash
cp .env.example .env
```

Edita el fitxer `.env` amb la teva configuració:

```bash
# Configuració del dispositiu Bluetti
BLUETTI_MAC=XX:XX:XX:XX:XX:XX
ENCRYPTION_KEY_FILE=encryption_keys.json

# Configuració MQTT
MQTT_HOST=192.168.1.100
MQTT_PORT=1883
MQTT_USERNAME=mqttuser
MQTT_PASSWORD=mqttpass
MQTT_TOPIC=bluetti

# Configuració de logging
LOG_LEVEL=info
```

## Execució amb Docker

Si prefereixes utilitzar el contenidor publicat a GHCR, pots fer-ho de forma molt senzilla. El contenidor necessita accés al socket de D-Bus del sistema per parlar amb BlueZ (Bluetooth) i la xarxa en mode host per simplificar la descoberta i evitar problemes de ports.

### `docker run`

```bash
docker run -d \
   --name bluetti-mqtt \
   --network host \
   -v /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket:ro \
   -v $(pwd)/config:/app/config \
   -v $(pwd)/logs:/app/logs \
   -e BLUETTI_MAC=XX:XX:XX:XX:XX:XX \
   -e MQTT_HOST=192.168.1.100 \
   -e MQTT_PORT=1883 \
   -e MQTT_USERNAME=usuari \
   -e MQTT_PASSWORD=contrasenya \
   -e MQTT_TOPIC=bluetti \
   -e LOG_LEVEL=info \
   -e ENCRYPTION_KEY_FILE=/app/config/encryption_keys.json \
   ghcr.io/jordigrasvi/bluetti-elite200v2-mqtt:latest
```

### `docker-compose.yml` d'exemple

```yaml
services:
   bluetti:
      image: ghcr.io/jordigrasvi/bluetti-elite200v2-mqtt:latest
      container_name: bluetti-mqtt
      network_mode: host
      restart: unless-stopped
      environment:
         BLUETTI_MAC: "XX:XX:XX:XX:XX:XX"  # Substitueix per la MAC real
         MQTT_HOST: "192.168.1.100"
         MQTT_PORT: "1883"
         MQTT_USERNAME: "usuari"
         MQTT_PASSWORD: "contrasenya"
         MQTT_TOPIC: "bluetti"
         LOG_LEVEL: "info"
         ENCRYPTION_KEY_FILE: "/app/config/encryption_keys.json"
      volumes:
         - ./config:/app/config
         - ./logs:/app/logs
         - /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket:ro
```

Després només cal executar:

```bash

```

### Notes de seguretat
- No posis credencials sensibles al repositori; utilitza un fitxer `.env` local o un secret manager si cal.
- El mode `host` és el més senzill per BLE + MQTT local. Si vols restringir-lo, pots provar `network_mode: bridge` i exposar només els ports MQTT si algun dia el contenidor actués de broker (ara no cal).
- El socket D-Bus es munta en mode lectura (`:ro`).

### Actualització de la imatge

```bash
## Configuració
docker compose up -d --force-recreate
```

Per fixar una versió exacta, substitueix `:latest` pel digest:

```bash
image: ghcr.io/jordigrasvi/bluetti-elite200v2-mqtt@sha256:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```


### Obtenció de l'adreça MAC del dispositiu

Per trobar l'adreça MAC del teu dispositiu Bluetti:

```bash
python -m bluetti_mqtt.discovery_cli --scan
```

Això mostrarà tots els dispositius Bluetti disponibles:

```
Found AC3001234567890123: address XX:XX:XX:XX:XX:XX
```

### Configuració de les claus d'encriptació

**IMPORTANT**: Per a la seguretat del teu dispositiu, necessitaràs obtenir les claus d'encriptació específiques del teu dispositiu Bluetti Elite 200 V2. Aquestes claus són úniques per a cada dispositiu i són necessàries per establir una comunicació segura.

#### Mètode 1: Utilitzant el mòdul oficial de criptografia Bluetti

Aquest és el mètode recomanat i més segur:

1. **Descarrega el mòdul oficial**:
   - Visita el lloc web oficial de Bluetti
   - Cerca "Bluetti Crypt Module Linux" o contacta amb el suport tècnic
   - Descarrega el fitxer `Bluetti_Crypt_Module_Linux-X.X.X.tar.gz`

2. **Extreu i instal·la el mòdul**:
   ```bash
   tar -xzf Bluetti_Crypt_Module_Linux-X.X.X.tar.gz
   # Segueix les instruccions d'instal·lació del mòdul
   ```

3. **Genera les claus del teu dispositiu**:
   - Utilitza les eines proporcionades pel mòdul oficial
   - Connecta't al teu dispositiu Elite 200 V2
   - Executa el procés d'autenticació per obtenir les claus

#### Mètode 2: Captura de tràfic Bluetooth (Avançat)

**Advertència**: Aquest mètode requereix coneixements tècnics avançats i pot ser complex.

##### Per a Android:
1. **Habilita el logging Bluetooth**:
   - Vés a `Configuració > Opcions de desenvolupador`
   - Activa "Registre HCI Bluetooth"

2. **Captura el tràfic**:
   - Instal·la l'aplicació oficial Bluetti
   - Connecta't al teu dispositiu Elite 200 V2
   - Realitza algunes operacions (llegir estat, canviar configuració)
   - El log es guardarà a `/sdcard/btsnoop_hci.log`

3. **Analitza el tràfic**:
   - Transfereix el fitxer `btsnoop_hci.log` al teu ordinador
   - Utilitza Wireshark per obrir i analitzar el fitxer
   - Cerca els paquets d'autenticació i handshake
   - Extreu les claus d'encriptació dels paquets capturats

##### Per a iOS:
1. **Configura el dispositiu per a desenvolupament**:
   - Necessitaràs un compte de desenvolupador d'Apple
   - Instal·la el perfil de configuració per a logging Bluetooth

2. **Captura i analitza**:
   - Similar al procés d'Android però utilitzant les eines d'Apple

#### Mètode 3: Enginyeria inversa del firmware (Molt avançat)

**Advertència**: Aquest mètode és només per a experts i pot invalidar la garantia.

1. **Extracció del firmware**:
   - Desmunta el dispositiu (invalida la garantia)
   - Connecta't al chip de memòria flash
   - Extreu el firmware utilitzant eines especialitzades

2. **Anàlisi del firmware**:
   - Utilitza eines com Ghidra, IDA Pro o Radare2
   - Cerca les funcions de criptografia i autenticació
   - Extreu les claus hardcoded o l'algoritme de generació

#### Format del fitxer encryption_keys.json

Un cop obtinguis les claus, crea el fitxer `encryption_keys.json` amb aquest format:

```json
{
  "XX:XX:XX:XX:XX:XX": {
    "pin": "000000",
    "key": "4a942a522abf710b3c8e61973e3aa17a",
    "token": "45b31b6c213dfcc16059010bb107746aa4dbb51589e9192e1b37dd0422e7e30d0cc071dcdbd3fd720928d65ee0ef8e1a"
  }
}
```

On:
- `XX:XX:XX:XX:XX:XX`: L'adreça MAC del teu dispositiu
- `pin`: El PIN del dispositiu (normalment "000000" per defecte)
- `key`: Clau d'encriptació de 32 caràcters hexadecimals (16 bytes)
- `token`: Token d'autenticació de 64+ caràcters hexadecimals

#### Verificació de les claus

Per verificar que les claus són correctes, pots utilitzar l'eina de test inclosa:

```bash
python test_encryption.py
```

Si les claus són correctes, hauràs de veure missatges com:
```
✅ Connexió establerta correctament
✅ Autenticació exitosa
✅ Dades desencriptades correctament
```

#### Resolució de problemes amb les claus

**Error: "Authentication failed"**
- Verifica que l'adreça MAC sigui correcta
- Comprova que el PIN sigui correcte
- Assegura't que la clau tingui exactament 32 caràcters hexadecimals

**Error: "Decryption failed"**
- Verifica que el token sigui correcte i complet
- Comprova que no hi hagi espais o caràcters extra
- Assegura't que el token estigui en format hexadecimal

**Error: "Device not found"**
- Verifica que el dispositiu estigui encès i a prop
- Comprova que no hi hagi altres aplicacions connectades
- Reinicia el Bluetooth del sistema

**Nota important**: Les claus mostrades en aquest exemple són fictícies. Cada dispositiu Bluetti té les seves pròpies claus úniques que has d'obtenir seguint un dels mètodes descrits anteriorment.

#### Obtenció de la llicència del dispositiu (Mètode alternatiu)

Si tens accés al mòdul oficial de Bluetti, també pots generar un fitxer de llicència del dispositiu:

1. **Genera la llicència**:
   ```bash
   # Utilitzant el mòdul oficial de Bluetti
   ./bluetti_license_generator --device [MAC_ADDRESS] --output bluetti_device_licence.csv
   ```

2. **Format del fitxer de llicència**:
   ```
   bluetti
   [TIMESTAMP]
   [MD5_KEY]
   [ENCRYPTION_KEY]
   ```

   On:
   - `TIMESTAMP`: Timestamp de generació de la llicència
   - `MD5_KEY`: Clau MD5 de 32 caràcters hexadecimals
   - `ENCRYPTION_KEY`: Clau d'encriptació completa (molt llarga)

3. **Conversió a format JSON**:
   Si tens el fitxer de llicència, pots convertir-lo al format JSON necessari:
   ```bash
   python convert_license.py bluetti_device_licence.csv
   ```

#### Eines d'ajuda incloses

El repositori inclou diverses eines per ajudar-te amb l'obtenció i verificació de les claus:

- `tools/extract_keys.py`: Extreu claus des de logs de Bluetooth
- `tools/verify_keys.py`: Verifica que les claus siguin correctes
- `tools/convert_license.py`: Converteix fitxers de llicència a format JSON
- `tools/test_connection.py`: Prova la connexió amb el dispositiu

## Ús

### Execució bàsica

```bash
python -m bluetti_mqtt.server_cli --broker [MQTT_BROKER_HOST] [MAC_ADDRESS]
```

### Amb autenticació MQTT

```bash
python -m bluetti_mqtt.server_cli --broker [MQTT_BROKER_HOST] --username [USERNAME] --password [PASSWORD] [MAC_ADDRESS]
```

### Amb interval de polling personalitzat

```bash
python -m bluetti_mqtt.server_cli --broker [MQTT_BROKER_HOST] --interval 60 [MAC_ADDRESS]
```

### Múltiples dispositius

```bash
python -m bluetti_mqtt.server_cli --broker [MQTT_BROKER_HOST] [MAC_ADDRESS_1] [MAC_ADDRESS_2]
```

## Integració amb Home Assistant

L'aplicació suporta el descobriment automàtic de Home Assistant. Les entitats apareixeran automàticament a Home Assistant si:

1. Home Assistant està configurat per utilitzar el mateix broker MQTT
2. El descobriment MQTT està habilitat (per defecte)

### Topics MQTT

- **Estat**: `bluetti/state/[DEVICE_NAME]/[PROPERTY]`
- **Comandes**: `bluetti/command/[DEVICE_NAME]/[PROPERTY]`
- **Descobriment HA**: `homeassistant/sensor/bluetti_[DEVICE_NAME]/[PROPERTY]/config`

### Propietats disponibles

- `battery_percent`: Percentatge de bateria
- `ac_output_power`: Potència de sortida AC (W)
- `dc_output_power`: Potència de sortida DC (W)
- `ac_input_power`: Potència d'entrada AC (W)
- `dc_input_power`: Potència d'entrada DC (W)
- `battery_voltage`: Voltatge de la bateria (V)
- `battery_current`: Corrent de la bateria (A)
- `temperature`: Temperatura del dispositiu (°C)

## Servei del sistema (systemd)

Per executar l'aplicació com a servei del sistema:

1. Crea el fitxer de servei:

```bash
sudo nano /etc/systemd/system/bluetti-mqtt.service
```

2. Afegeix el contingut següent:

```ini
[Unit]
Description=Bluetti MQTT Bridge
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=30
TimeoutStopSec=15
User=pi
WorkingDirectory=/home/pi/bluetti-elite200v2-mqtt
ExecStart=/home/pi/bluetti-elite200v2-mqtt/venv/bin/python -m bluetti_mqtt.server_cli --broker 192.168.1.100 XX:XX:XX:XX:XX:XX

[Install]
WantedBy=multi-user.target
```

3. Habilita i inicia el servei:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bluetti-mqtt
sudo systemctl start bluetti-mqtt
```

## Desenvolupament i Debug

### Logging detallat

```bash
python -m bluetti_mqtt.server_cli --broker [MQTT_BROKER_HOST] -v [MAC_ADDRESS]
```

### Captura de dades per a anàlisi

```bash
python -m bluetti_mqtt.logger_cli --log capture.log [MAC_ADDRESS]
```

### Descobriment de nous registres

```bash
python -m bluetti_mqtt.discovery_cli --log discovery.log [MAC_ADDRESS]
```

## Resolució de problemes

### El dispositiu no es connecta

1. Verifica que l'adreça MAC sigui correcta
2. Assegura't que el dispositiu estigui a prop (< 10 metres)
3. Comprova que no hi hagi altres aplicacions connectades al dispositiu
4. Verifica les claus d'encriptació

### Errors d'autenticació

1. Verifica el fitxer `encryption_keys.json`
2. Assegura't que les claus siguin correctes per al teu dispositiu específic
3. Comprova que el PIN sigui correcte

### Problemes de MQTT

1. Verifica la connectivitat amb el broker MQTT
2. Comprova les credencials d'autenticació
3. Verifica els permisos dels topics

## Contribució

Les contribucions són benvingudes! Si us plau:

1. Fes un fork del projecte
2. Crea una branca per a la teva funcionalitat
3. Fes commit dels teus canvis
4. Fes push a la branca
5. Obre un Pull Request

## Llicència

Aquest projecte està llicenciat sota la llicència MIT. Veure el fitxer [LICENSE](LICENSE) per a més detalls.

## Agraïments

- [bluetti_mqtt](https://github.com/warhammerkid/bluetti_mqtt) - Projecte base per a la comunicació amb dispositius Bluetti
- Comunitat de desenvolupadors de Home Assistant
- Bluetti per proporcionar el mòdul de criptografia

## Avís legal

Aquest projecte no està afiliat oficialment amb Bluetti. Utilitza'l sota la teva pròpia responsabilitat. L'ús incorrecte pot afectar la garantia del teu dispositiu.

## Suport

Si tens problemes o preguntes:

1. Revisa la secció de [Resolució de problemes](#resolució-de-problemes)
2. Cerca als [Issues](https://github.com/JordiGrasvi/bluetti-elite200v2-mqtt/issues) existents
3. Crea un nou issue si no trobes solució

---

**Nota important sobre la privacitat**: Aquest README no conté cap dada privada. Totes les claus d'encriptació, adreces MAC i credencials mostrades són exemples i han de ser substituïdes per les teves dades reals.