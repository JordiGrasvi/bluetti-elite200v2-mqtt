#!/bin/bash
# Script d'instal·lació Bluetti MQTT Bridge per VM Debian/Ubuntu
set -e

# 1. Actualitza paquets
apt update && apt upgrade -y

# 2. Instal·la Docker i Docker Compose
apt install -y docker.io docker-compose

# 3. Instal·la Python, BlueZ i utilitats
apt install -y python3 python3-pip bluez

# 4. Dona permisos al dispositiu Bluetooth (si existeix)
if [ -e /dev/hci0 ]; then
  chmod 666 /dev/hci0
fi

# 5. Inicia el servei Bluetooth
systemctl enable bluetooth
systemctl start bluetooth

# 6. Comprova el dispositiu Bluetooth
hciconfig -a || echo "No s'ha trobat /dev/hci0. Comprova el passthrough USB."

# 7. Crea carpetes de projecte si no existeixen
mkdir -p /root/bluetti
mkdir -p /root/docker

# 8. (Opcional) Instal·la dependències Python si cal
if [ -f /root/bluetti/requirements.txt ]; then
  pip3 install -r /root/bluetti/requirements.txt
fi

# 9. Inicia el Docker Compose
if [ -f /root/docker/docker-compose.yml ]; then
  docker compose -f /root/docker/docker-compose.yml up -d
else
  echo "No trobat /root/docker/docker-compose.yml. Copia'l abans d'executar el script."
fi

# 10. Mostra l'estat del contenidor
sleep 2
docker ps --format '{{.Names}}'

echo "Instal·lació finalitzada. Comprova els logs amb: docker logs --tail 100 <nom_contenidor>"
