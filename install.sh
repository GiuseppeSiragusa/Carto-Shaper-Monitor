#!/bin/bash

# Carto Shaper Monitor - Script di Installazione Automatica
# Questo script installa e configura il monitoraggio dell'Input Shaper
# basato sull'accelerometro del Cartographer.

set -e

# --- Colori per l'output ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Carto Shaper Monitor - Installazione ===${NC}"

# --- 1. Verifica che l'utente non sia root ---
if [ "$EUID" -eq 0 ]; then
  echo -e "${RED}Errore: Non eseguire questo script come root.${NC}"
  echo "Esegui come utente normale (es. 'pi'). Lo script userà 'sudo' quando necessario."
  exit 1
fi

# --- 2. Installa le dipendenze Python ---
echo -e "${YELLOW}Installazione delle dipendenze Python...${NC}"
sudo apt-get update
sudo apt-get install -y python3-pip
pip3 install -r requirements.txt

# --- 3. Copia lo script principale ---
echo -e "${YELLOW}Copia dello script principale in /home/pi/...${NC}"
cp carto_shaper_monitor.py /home/pi/carto_shaper_monitor.py
chmod +x /home/pi/carto_shaper_monitor.py

# --- 4. Installa il servizio systemd ---
echo -e "${YELLOW}Installazione del servizio systemd...${NC}"
sudo cp config/carto-shaper.service /etc/systemd/system/carto-shaper.service

# Sostituisci l'utente nel file di servizio con l'utente corrente
CURRENT_USER=$(whoami)
sudo sed -i "s|User=pi|User=$CURRENT_USER|g" /etc/systemd/system/carto-shaper.service
sudo sed -i "s|/home/pi/|/home/$CURRENT_USER/|g" /etc/systemd/system/carto-shaper.service

# --- 5. Abilita e avvia il servizio ---
echo -e "${YELLOW}Abilitazione e avvio del servizio...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable carto-shaper.service
sudo systemctl start carto-shaper.service

# --- 6. Verifica lo stato ---
sleep 2
echo -e "${GREEN}=== Installazione completata! ===${NC}"
echo "Stato del servizio:"
sudo systemctl status carto-shaper.service --no-pager

echo -e "\n${GREEN}Il monitoraggio è ora attivo e verrà avviato automaticamente ad ogni riavvio.${NC}"
echo "Per controllare i log in tempo reale: sudo journalctl -u carto-shaper.service -f"
echo "Per fermare il servizio: sudo systemctl stop carto-shaper.service"