import math
import psutil
import platform

class PowerModel:
    def __init__(self):
        self.clock_frequency = 0
        self.num_cores = 0
        self.activity_factor = 0
        self.supply_voltage = 0

    def get_system_info(self):
        self.clock_frequency = psutil.cpu_freq().current 
        self.num_cores = psutil.cpu_count(logical=False)
        self.activity_factor = psutil.cpu_percent(interval=1) / (100 * self.num_cores)

        if platform.system() == 'Windows':
            from Utils import windows_utils
            self.clock_frequency =windows_utils. get_clock_frequency()
            self.supply_voltage = windows_utils.get_supply_voltage()
        elif platform.system() == 'Linux':
            from Utils import linux_utils
            self.clock_frequency = linux_utils.get_clock_frequency()
            self.supply_voltage = linux_utils.get_supply_voltage()
        else:
            raise Exception("Unsupported operating system")

    def estimate_power_consumption(self, pid):
        process = psutil.Process(pid)
        memory_info = process.memory_info()
        capacitive_load = memory_info.rss / self.num_cores
        dynamic_power = 0.5 * capacitive_load * math.pow(self.supply_voltage, 2) * self.clock_frequency * self.activity_factor
        return dynamic_power
