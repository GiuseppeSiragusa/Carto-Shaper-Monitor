#!/usr/bin/env python3
"""
carto_shaper_monitor.py
Monitoraggio vibrazioni tramite accelerometro del Cartographer.
Analizza i dati e aggiorna l'Input Shaper SOLO al cambio layer.
"""

import asyncio
import json
import numpy as np
import websockets
from datetime import datetime

# ==================== CONFIGURAZIONE ====================
MOONRAKER_URL = "ws://localhost:7125/websocket"
SENSOR_NAME = "adxl345"

# Parametri di analisi
SAMPLE_RATE = 3200
FFT_WINDOW_SEC = 2.0          # Secondi di dati da analizzare al cambio layer
FREQ_MIN = 10.0
FREQ_MAX = 150.0
FREQ_DELTA_THRESHOLD = 1.5    # Hz - soglia minima per aggiornare

# Frequenze attuali
current_freq_x = None
current_freq_y = None
last_layer = -1

# ==================== BUFFER GLOBALE ====================
buffer_x = []
buffer_y = []
max_samples = int(SAMPLE_RATE * FFT_WINDOW_SEC)


# ==================== CONNESSIONE E COMANDI ====================
async def send_gcode(ws, gcode):
    """Invia un comando G-code a Klipper tramite Moonraker."""
    await ws.send(json.dumps({
        "jsonrpc": "2.0",
        "method": "printer.gcode.script",
        "params": {"script": gcode},
        "id": 1
    }))


async def subscribe_accelerometer(ws):
    """Sottoscrive lo streaming dei dati dall'accelerometro."""
    await ws.send(json.dumps({
        "jsonrpc": "2.0",
        "method": "adxl345/dump_adxl345",
        "params": {"sensor": SENSOR_NAME},
        "id": 2
    }))


async def subscribe_print_stats(ws):
    """Sottoscrive le notifiche di stato di print_stats (contiene current_layer)."""
    await ws.send(json.dumps({
        "jsonrpc": "2.0",
        "method": "printer.objects.subscribe",
        "params": {
            "objects": {
                "print_stats": ["current_layer", "total_layer"]
            }
        },
        "id": 3
    }))


# ==================== ANALISI FFT ====================
def compute_fft(samples_x, samples_y, sample_rate):
    """Calcola la FFT e restituisce le frequenze dominanti per X e Y."""
    n = len(samples_x)
    if n < 128:
        return None, None

    window = np.hanning(n)

    fft_x = np.fft.rfft(samples_x * window)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    magnitude_x = np.abs(fft_x)

    fft_y = np.fft.rfft(samples_y * window)
    magnitude_y = np.abs(fft_y)

    mask = (freqs >= FREQ_MIN) & (freqs <= FREQ_MAX)
    freqs_band = freqs[mask]
    mag_x_band = magnitude_x[mask]
    mag_y_band = magnitude_y[mask]

    if len(freqs_band) == 0:
        return None, None

    peak_x = freqs_band[np.argmax(mag_x_band)]
    peak_y = freqs_band[np.argmax(mag_y_band)]

    return peak_x, peak_y


# ==================== AGGIORNAMENTO INPUT SHAPER ====================
async def update_input_shaper(ws, freq_x, freq_y):
    """Invia SET_INPUT_SHAPER solo se la variazione supera la soglia."""
    global current_freq_x, current_freq_y

    if current_freq_x is not None and current_freq_y is not None:
        delta_x = abs(freq_x - current_freq_x)
        delta_y = abs(freq_y - current_freq_y)
        if delta_x < FREQ_DELTA_THRESHOLD and delta_y < FREQ_DELTA_THRESHOLD:
            return False

    freq_x = round(freq_x, 1)
    freq_y = round(freq_y, 1)

    gcode = f"SET_INPUT_SHAPER SHAPER_FREQ_X={freq_x} SHAPER_FREQ_Y={freq_y}"
    await send_gcode(ws, gcode)

    current_freq_x = freq_x
    current_freq_y = freq_y

    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
          f"Input Shaper aggiornato: X={freq_x} Hz, Y={freq_y} Hz")
    return True


# ==================== GESTIONE CAMBIO LAYER ====================
async def on_layer_change(ws):
    """Eseguita quando viene rilevato un cambio layer."""
    global buffer_x, buffer_y

    if len(buffer_x) < 128:
        print("Dati insufficienti per l'analisi al cambio layer.")
        return

    # Prendi gli ultimi max_samples campioni
    samples_x = np.array(buffer_x[-max_samples:])
    samples_y = np.array(buffer_y[-max_samples:])

    freq_x, freq_y = compute_fft(samples_x, samples_y, SAMPLE_RATE)

    if freq_x and freq_y:
        await update_input_shaper(ws, freq_x, freq_y)
    else:
        print("FFT non valida al cambio layer.")


# ==================== LOOP PRINCIPALE ====================
async def monitor_loop():
    global buffer_x, buffer_y, last_layer

    async with websockets.connect(MOONRAKER_URL) as ws:
        print("Connesso a Moonraker.")
        await subscribe_accelerometer(ws)
        await subscribe_print_stats(ws)
        print("In attesa di cambi layer...")

        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(msg)

                # --- Dati accelerometro ---
                if "params" in data and "data" in data["params"]:
                    for row in data["params"]["data"]:
                        buffer_x.append(row[1])
                        buffer_y.append(row[2])

                    if len(buffer_x) > max_samples:
                        buffer_x = buffer_x[-max_samples:]
                        buffer_y = buffer_y[-max_samples:]

                # --- Notifica di stato (print_stats) ---
                if data.get("method") == "notify_status_update":
                    params = data.get("params", [{}])
                    if params and isinstance(params[0], dict):
                        stats = params[0].get("print_stats")
                        if stats and "current_layer" in stats:
                            layer = stats["current_layer"]
                            if layer is not None and layer != last_layer:
                                last_layer = layer
                                print(f"\n--- Cambio layer rilevato: {layer} ---")
                                await on_layer_change(ws)

            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                print("Connessione chiusa.")
                break


# ==================== AVVIO ====================
if __name__ == "__main__":
    print("Avvio monitoraggio vibrazioni Cartographer (cambio layer)...")
    print(f"URL: {MOONRAKER_URL}")
    print(f"Sensore: {SENSOR_NAME}")
    print(f"Finestra FFT: {FFT_WINDOW_SEC}s")
    print("-" * 50)

    try:
        asyncio.run(monitor_loop())
    except KeyboardInterrupt:
        print("\nArresto manuale.")