#!/bin/bash

# Script d'instal·lació automàtica per a Bluetti Elite 200 V2 MQTT Bridge
# Ús: curl -sSL https://raw.githubusercontent.com/JordiGrasvi/bluetti-elite200v2-mqtt/main/install.sh | bash

set -e

# Colors per a la sortida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funcions d'utilitat
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Variables
INSTALL_DIR="$HOME/bluetti-elite200v2-mqtt"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_NAME="bluetti-mqtt"

print_info "Instal·lant Bluetti Elite 200 V2 MQTT Bridge..."

# Comprova si Python 3.7+ està instal·lat
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no està instal·lat. Si us plau, instal·la Python 3.7 o superior."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.7"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
    print_error "Python $PYTHON_VERSION detectat. Es requereix Python $REQUIRED_VERSION o superior."
    exit 1
fi

print_success "Python $PYTHON_VERSION detectat"

# Comprova si git està instal·lat
if ! command -v git &> /dev/null; then
    print_error "Git no està instal·lat. Si us plau, instal·la git primer."
    exit 1
fi

# Clona o actualitza el repositori
if [ -d "$INSTALL_DIR" ]; then
    print_info "Actualitzant repositori existent..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    print_info "Clonant repositori..."
    git clone https://github.com/JordiGrasvi/bluetti-elite200v2-mqtt.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Crea entorn virtual
print_info "Creant entorn virtual..."
python3 -m venv "$VENV_DIR"

# Activa entorn virtual
source "$VENV_DIR/bin/activate"

# Actualitza pip
print_info "Actualitzant pip..."
pip install --upgrade pip

# Instal·la dependències
print_info "Instal·lant dependències..."
pip install -r requirements.txt

# Instal·la el paquet en mode desenvolupament
print_info "Instal·lant bluetti-mqtt..."
pip install -e .

print_success "Instal·lació completada!"

# Configuració inicial
print_info "Configurant aplicació..."

# Copia fitxers d'exemple si no existeixen
if [ ! -f ".env" ]; then
    cp ".env.example" ".env"
    print_info "Fitxer .env creat des de l'exemple"
fi

if [ ! -f "encryption_keys.json" ]; then
    cp "encryption_keys.json.example" "encryption_keys.json"
    print_info "Fitxer encryption_keys.json creat des de l'exemple"
fi

print_warning "IMPORTANT: Configura els fitxers .env i encryption_keys.json amb les teves dades"

# Ofereix crear servei systemd
echo
read -p "Vols crear un servei systemd per executar automàticament? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Creant servei systemd..."
    
    # Demana configuració
    read -p "Introdueix l'adreça MAC del dispositiu Bluetti: " MAC_ADDRESS
    read -p "Introdueix l'adreça del broker MQTT: " MQTT_BROKER
    
    # Crea fitxer de servei
    sudo tee "/etc/systemd/system/$SERVICE_NAME.service" > /dev/null <<EOF
[Unit]
Description=Bluetti Elite 200 V2 MQTT Bridge
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=30
TimeoutStopSec=15
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$VENV_DIR/bin/python -m bluetti_mqtt.server_cli --broker $MQTT_BROKER $MAC_ADDRESS
Environment=PATH=$VENV_DIR/bin

[Install]
WantedBy=multi-user.target
EOF

    # Recarrega systemd i habilita servei
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    
    print_success "Servei systemd creat i habilitat"
    print_info "Pots iniciar el servei amb: sudo systemctl start $SERVICE_NAME"
    print_info "Veure logs amb: sudo journalctl -u $SERVICE_NAME -f"
fi

# Mostra informació final
echo
print_success "🎉 Instal·lació completada!"
echo
print_info "Passos següents:"
echo "1. Edita $INSTALL_DIR/.env amb la configuració MQTT"
echo "2. Configura $INSTALL_DIR/encryption_keys.json amb les claus del dispositiu"
echo "3. Prova la connexió: cd $INSTALL_DIR && $VENV_DIR/bin/python tools/test_connection.py"
echo "4. Executa l'aplicació: cd $INSTALL_DIR && $VENV_DIR/bin/python -m bluetti_mqtt.server_cli --broker [MQTT_HOST] [MAC_ADDRESS]"
echo
print_info "Documentació completa: $INSTALL_DIR/README.md"
print_info "Eines d'ajuda disponibles a: $INSTALL_DIR/tools/"

if command -v systemctl &> /dev/null && systemctl is-enabled "$SERVICE_NAME" &> /dev/null; then
    echo
    print_info "Servei systemd configurat. Comandes útils:"
    echo "  sudo systemctl start $SERVICE_NAME    # Inicia el servei"
    echo "  sudo systemctl stop $SERVICE_NAME     # Para el servei"
    echo "  sudo systemctl status $SERVICE_NAME   # Estat del servei"
    echo "  sudo journalctl -u $SERVICE_NAME -f   # Veure logs en temps real"
fi