from input_shaper_parser import read_input_shaper
import time

def update_ui(data):
    print("=== INPUT SHAPER ===")
    print(f"X: {data['shaper_type_x']} @ {data['shaper_freq_x']} Hz (damp {data['damping_ratio_x']})")
    print(f"Y: {data['shaper_type_y']} @ {data['shaper_freq_y']} Hz (damp {data['damping_ratio_y']})")
    print("====================")

def main():
    while True:
        data = read_input_shaper()
        if data:
            update_ui(data)
        else:
            print("Input shaper non trovato nel printer.cfg")
        time.sleep(5)

if __name__ == "__main__":
    main()
