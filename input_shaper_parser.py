import configparser
import os

PRINTER_CFG = "/home/pi/printer_data/config/printer.cfg"

def read_input_shaper():
    if not os.path.exists(PRINTER_CFG):
        return None

    cfg = configparser.ConfigParser()
    cfg.read(PRINTER_CFG)

    if "input_shaper" not in cfg:
        return None

    section = cfg["input_shaper"]

    return {
        "shaper_type_x": section.get("shaper_type_x"),
        "shaper_freq_x": section.getfloat("shaper_freq_x"),
        "damping_ratio_x": section.getfloat("damping_ratio_x"),
        "shaper_type_y": section.get("shaper_type_y"),
        "shaper_freq_y": section.getfloat("shaper_freq_y"),
        "damping_ratio_y": section.getfloat("damping_ratio_y"),
    }
