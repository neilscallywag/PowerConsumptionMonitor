import concurrent.futures
import multiprocessing
import numpy as np
import psutil
import GPUtil
import platform
import time

class PowerModel:
    def __init__(self):
        self.clock_frequency = 0
        self.num_cores = 0
        self.supply_voltage = 0

    def get_system_info(self):
        self.clock_frequency = psutil.cpu_freq().current
        self.num_cores = psutil.cpu_count(logical=False)
        if platform.system() == 'Windows':
            from Utils import windows_utils
            self.clock_frequency = windows_utils.get_clock_frequency()
            self.supply_voltage = windows_utils.get_supply_voltage()
        elif platform.system() == 'Linux':
            from Utils import linux_utils
            self.clock_frequency = linux_utils.get_clock_frequency()
            self.supply_voltage = linux_utils.get_supply_voltage()
        else:
            raise Exception("Unsupported operating system")

    def estimate_power_consumption(self, pid):
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        processes = [parent] + children
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.estimate_power_for_process, processes)

        total_power = sum(results)
        return total_power

    def estimate_power_for_process(self, process):
        # Modify capacitive load based on processor documentation or existing models
        capacitive_load = 1 / 1000  # 1 micro farad
        capacitor_energy = self.capacitor_energy(capacitive_load, self.supply_voltage)

        # Increase the duration for better representation of the average activity factor
        duration = 10  # Increase duration as needed
        interval = 1

        with concurrent.futures.ThreadPoolExecutor() as executor:
            cpu = executor.map(self.activity_factor_cpu, [(process, interval, duration)])
        with concurrent.futures.ThreadPoolExecutor() as executor:
            gpu = executor.map(self.activity_factor_gpu, [(process, interval, duration)])

        activity_factor_cpu = list(cpu)[0]
        activity_factor_gpu = list(gpu)[0]

        dynamic_power = (capacitor_energy * (activity_factor_cpu + activity_factor_gpu))

        # Include static power estimation
        k = 1e-6  # Constant for static power, adjust according to processor technology
        temperature = 25 + 273.15  # Assuming room temperature (in Kelvin), consider using temperature sensors
        static_power = k * self.supply_voltage ** 2 * temperature

        # Total power is the sum of dynamic and static power
        total_power = dynamic_power + static_power

        return total_power * 60 * 60 

    def capacitor_energy(self, capacitance, voltage):
        return 0.5 * capacitance * voltage * voltage

    def activity_factor_cpu(self, tup):
        process, interval, duration = tup[0], tup[1], tup[2]
        cpu_percentages = []
        for _ in range(int(duration / interval)):
            cpu_percentages.append(process.cpu_percent(interval=interval))
            time.sleep(interval)
        cpu_percent_end = process.cpu_percent(interval=None)
        activity_factor = abs((cpu_percent_end - np.mean(cpu_percentages))) / 100.0
        return activity_factor

    def activity_factor_gpu(self, tup):
        process, interval, duration = tup[0], tup[1], tup[2]
        try:
            gpu_percentages = []
            for _ in range(int(duration / interval)):
                gpu_list = GPUtil.getGPUs()
                for gpu in gpu_list:
                    for proc in gpu.getProcessUtilization(interval=interval):
                        if proc.pid ==                         process.pid:
                            gpu_percentages.append(proc.gpuUtil)
                            time.sleep(interval)
            gpu_percent_end = 0.0
            for gpu in gpu_list:
                for proc in gpu.getProcessUtilization(interval=None):
                    if proc.pid == process.pid:
                        gpu_percent_end = proc.gpuUtil
            activity_factor = abs((gpu_percent_end - np.mean(gpu_percentages))) / 100.0
        except:
            activity_factor = 0.0
        return activity_factor


