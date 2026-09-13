# Carto Shaper Monitor

Monitoraggio adattivo dell'Input Shaper tramite l'accelerometro integrato nel Cartographer. Aggiorna automaticamente le frequenze di risonanza durante la stampa, **senza modificare lo slicer**.

## 📋 Prerequisiti

- Klipper installato e funzionante
- Moonraker attivo
- Cartographer con accelerometro ADXL345 (o LIS2DW) già configurato
- Python 3.8+ con `numpy` e `websockets`

## 🔧 Installazione Automatica

Clona la repository ed esegui lo script di installazione:

```bash
git clone https://github.com/GiuseppeSiragusa/Carto-Shaper-Monitor.git
cd Carto-Shaper-Monitor
chmod +x install.sh
./install.sh
