import subprocess

def get_clock_frequency():
    p = subprocess.Popen(['wmic', 'cpu', 'get', 'CurrentClockSpeed'], stdout=subprocess.PIPE)
    output = p.stdout.readlines()
    return float(output[1].decode().strip())/ 1e9

def get_supply_voltage():
    # Use the default value for Windows
    return 2
