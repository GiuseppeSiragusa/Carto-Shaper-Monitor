#!/bin/bash
echo "=== Carto Shaper Monitor - Installazione (AUTO-VENV) ==="

# Nome della cartella del virtual environment
VENV_DIR="venv"

# 1. Creazione del virtual environment se non esiste
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Nessun ambiente virtuale trovato. Creazione in corso..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Attivazione del virtual environment
echo "[INFO] Attivazione ambiente virtuale..."
source "$VENV_DIR/bin/activate"

# 3. Aggiornamento pip dentro il venv
echo "[INFO] Aggiornamento pip..."
pip install --upgrade pip

# 4. Installazione delle dipendenze Python
if [ -f "requirements.txt" ]; then
    echo "[INFO] Installazione dipendenze da requirements.txt..."
    pip install -r requirements.txt
else
    echo "[WARN] Nessun file requirements.txt trovato. Procedo senza installare dipendenze."
fi

# 5. Installazione del servizio systemd
if [ -f "carto_shaper_monitor.service" ]; then
    echo "[INFO] Installazione del servizio systemd..."
    sudo cp carto_shaper_monitor.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable carto_shaper_monitor.service
    sudo systemctl restart carto_shaper_monitor.service
else
    echo "[WARN] File carto_shaper_monitor.service non trovato. Servizio non installato."
fi

echo "=== Installazione completata con successo! ==="
