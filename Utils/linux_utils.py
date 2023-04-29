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
        for chip in sensors.iter_detected_chips():
            if chip.prefix == "coretemp":
                for feature in chip:
                    if feature.label == "Vcore":
                        supply_voltage = feature.get_value()
        sensors.cleanup()
        return supply_voltage
    
    def get_temperature():
        sensors.init()
        for chip in sensors.iter_detected_chips():
            if chip.prefix == "coretemp":
                for feature in chip:
                    if "temp" in feature.label:
                        temperature = feature.get_value()
        sensors.cleanup()
        return temperature
except ModuleNotFoundError:
    print("Sensors module not found")


