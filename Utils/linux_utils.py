import subprocess
try:
    import sensors
    def get_clock_frequency():
        freq_output = subprocess.check_output(["lscpu"])
        freq_lines = freq_output.decode().strip().split('\n')
        freq_line = next((line for line in freq_lines if 'CPU MHz' in line), None)
        if freq_line:
            return float(freq_line.split(':')[1].strip())
        else:
            return 0.0

    def get_supply_voltage():
        sensors.init()
        try:
            for chip in sensors.iter_detected_chips():
                for feature in chip:
                    if feature.label == "Vcore":
                        return float(feature.get_value())
        finally:
            sensors.cleanup()
        return 0.0

    
    def get_temperature():
        sensors.init()
        try:
            for chip in sensors.iter_detected_chips():
                for feature in chip:
                    if feature.label == "CPU Temp":
                        return float(feature.get_value())
        finally:
            sensors.cleanup()
        return 0.0
except ModuleNotFoundError:
    print("Sensors module not found")


