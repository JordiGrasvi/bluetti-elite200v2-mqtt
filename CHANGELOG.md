# Changelog

Tots els canvis notables d'aquest projecte es documentaran en aquest fitxer.

El format està basat en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
i aquest projecte segueix [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Afegit
- Suport inicial per a Bluetti Elite 200 V2
- Connexió Bluetooth amb encriptació
- Publicació de dades a MQTT
- Integració automàtica amb Home Assistant
- Eines d'ajuda per a l'obtenció de claus
- Documentació completa en català
- Scripts de verificació i test
- Suport per a múltiples dispositius
- Configuració via fitxers .env
- Servei systemd per a execució automàtica

### Característiques
- Monitorització en temps real de:
  - Percentatge de bateria
  - Potència AC/DC d'entrada i sortida
  - Voltatge i corrent de bateria
  - Temperatura del dispositiu
  - Estat de càrrega/descàrrega
- Descobriment automàtic de dispositius
- Logging configurable
- Gestió d'errors robusta
- Reconnexió automàtica

### Eines incloses
- `tools/convert_license.py`: Converteix fitxers de llicència a JSON
- `tools/verify_keys.py`: Verifica les claus d'encriptació
- `tools/test_connection.py`: Prova la connexió Bluetooth
- `tools/extract_keys.py`: Extreu claus des de logs Bluetooth

### Documentació
- README complet amb instruccions detallades
- Guies per obtenir claus d'encriptació
- Exemples de configuració
- Resolució de problemes comuns
- Instruccions d'instal·lació pas a pas