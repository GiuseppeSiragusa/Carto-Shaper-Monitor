import asyncio
import websockets
import json
import logging
import time

# ---------------------------------------------------------
# LOGGING PROFESSIONALE
# ---------------------------------------------------------
logging.basicConfig(
    filename="/var/log/carto_shaper_monitor.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info("Carto Shaper Monitor avviato.")

# ---------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------
WEBSOCKET_URL = "ws://localhost:7125/websocket"
RECONNECT_DELAY = 3  # secondi
MAX_RECONNECT_DELAY = 15  # limite massimo backoff

# ---------------------------------------------------------
# FUNZIONE DI CONNESSIONE
# ---------------------------------------------------------
async def connect():
    logging.info(f"Tentativo di connessione a {WEBSOCKET_URL}...")
    return await websockets.connect(WEBSOCKET_URL)

# ---------------------------------------------------------
# FUNZIONE PRINCIPALE DI MONITORAGGIO
# ---------------------------------------------------------
async def monitor():
    delay = RECONNECT_DELAY

    while True:
        try:
            ws = await connect()
            logging.info("Connessione stabilita.")

            # Reset del backoff
            delay = RECONNECT_DELAY

            # Richiesta iniziale
            await ws.send(json.dumps({"method": "machine.status"}))

            while True:
                message = await ws.recv()
                data = json.loads(message)

                # Log dei dati ricevuti
                logging.info(f"Dati ricevuti: {data}")

        except websockets.exceptions.ConnectionClosedError:
            logging.warning("Connessione chiusa dal server. Riconnessione...")
        except ConnectionRefusedError:
            logging.error("Server non raggiungibile. Riprovo...")
        except Exception as e:
            logging.error(f"Errore inatteso: {e}")

        # Backoff progressivo
        logging.info(f"Riconnessione tra {delay} secondi...")
        time.sleep(delay)
        delay = min(delay + 2, MAX_RECONNECT_DELAY)

# ---------------------------------------------------------
# AVVIO
# ---------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(monitor())
    except Exception as e:
        logging.critical(f"Errore critico: {e}")
