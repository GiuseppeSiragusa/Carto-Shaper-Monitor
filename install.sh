#!/bin/bash

echo "=== Carto Shaper Monitor - Installazione (AUTO-SERVICE) ==="

# 1. Creazione venv
if [ ! -d "venv" ]; then
    echo "[INFO] Nessun ambiente virtuale trovato. Creazione in corso..."
    python3 -m venv venv
fi

# 2. Attivazione venv
echo "[INFO] Attivazione ambiente virtuale..."
source venv/bin/activate

# 3. Aggiornamento pip
echo "[INFO] Aggiornamento pip..."
pip install --upgrade pip

# 4. Installazione dipendenze
echo "[INFO] Installazione dipendenze da requirements.txt..."
pip install -r requirements.txt

# 5. Installazione servizio systemd
SERVICE_FILE="config/carto_shaper_monitor.service"
TARGET="/etc/systemd/system/carto_shaper_monitor.service"

if [ -f "$SERVICE_FILE" ]; then
    echo "[INFO] Installazione servizio systemd..."
    sudo cp "$SERVICE_FILE" "$TARGET"
else
    echo "[ERROR] File di servizio non trovato: $SERVICE_FILE"
    exit 1
fi

# 6. Ricarica systemd
echo "[INFO] Ricarica systemd..."
sudo systemctl daemon-reload

# 7. Abilita il servizio
echo "[INFO] Abilitazione servizio..."
sudo systemctl enable carto_shaper_monitor.service

# 8. Avvia il servizio
echo "[INFO] Avvio servizio..."
sudo systemctl restart carto_shaper_monitor.service

# 9. Stato finale
echo "=== Stato del servizio ==="
systemctl status carto_shaper_monitor.service --no-pager
