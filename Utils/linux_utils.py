import subprocess
try:
    import sensors
    def get_clock_frequency():
        p = subprocess.Popen(['lscpu', '-p=cpu', '-e=CLOCK'], stdout=subprocess.PIPE)
        output = p.stdout.readlines()
        return float(output[1].decode().strip())/1e9

    def get_supply_voltage():
        sensors.init()
        for chip in sensors.iter_detected_chips():
            if chip.prefix == "coretemp":
                for feature in chip:
                    if feature.label == "Vcore":
                        supply_voltage = feature.get_value()
        sensors.cleanup()
        return supply_voltage
except ModuleNotFoundError:
    print("Sensors module not found")


