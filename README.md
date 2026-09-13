# Carto-Shaper Monitor (Printer.cfg Mode)

Questo monitor legge i valori dello shaper direttamente dal file `printer.cfg`,
compatibile con tutte le versioni moderne di Klipper e Moonraker.

## File inclusi

- `input_shaper_parser.py` → parser del printer.cfg
- `monitor.py` → monitor che aggiorna la UI
- `carto-shaper.service` → servizio systemd

## Installazione

```bash
sudo cp carto-shaper.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable carto-shaper.service
sudo systemctl start carto-shaper.service
