import concurrent.futures
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
            # One limitations to this temperature sensor approach is that it doesn't take into account variation of temperature as the 
            # process runs or even how much the process being tested impacts the temperature. 
            self.temperature = 25 #assume 25 degrees for windows. There is no good library to measure temperature without using shells
        elif platform.system() == 'Linux':
            from Utils import linux_utils
            self.clock_frequency = linux_utils.get_clock_frequency()
            self.supply_voltage = linux_utils.get_supply_voltage()
            self.temperature = linux_utils.get_temperature()
        else:
            raise Exception("Unsupported operating system")

    def estimate_power_consumption(self, pid):
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        # Do not for the love of god select systemd process on linux as it will recursively call all its children into the list 
        processes = [parent] + children

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.estimate_power_for_process, processes)

        total_power = sum(results)
        return total_power

    def estimate_power_for_process(self, process):
        """
        This is a very bad estimation because to accurately estimate you would need to have detailed information about the hardware
        used which cannot be determined using software. 

        There are also other things to consider such as overclocked processors, temperature changes, Wattage supplied etc.
        
        CPU Overclocked Watts = Default Watts x ( S0 / S ) * ( V0 / V ) ^ 2.
        Where,
        S0 = Overclocked Processor Speed,
        S = Default Processor Speed,
        V0 = Overclocked Processor Vcore Voltage,
        V = Default Processor Vcore Voltage.
        Processor Temperature = ( C/W Value x Overclocked Wattage) + Case Temperature.

        However, given we do not have access to all these informations. It is rather difficult to determine with any kind of practical accuracy.

        We could modify this to take in options from users to aid into the calculation. However, the above formula does not take into account individual processes.
        In practice, I would assume that even to determine the individual components per processes is extremly difficult.

        Another way I could think of is by calculating the io events and how much power is consumed by them. However, the challenge is that 
        you would need to have some reasonable assumptions to be made about the battery consumed per io event notwithstanding the fact that the value may
        not even be constant per IO event.

        //PS this is the best i could do in the short amount of time I have had. I asked the HR if it could be postponed as this task was
        // given to us during my finals exam. I could only allot 2-3 days doing this on a windows machine with limited computational resources.

        Sources: 
        https://community.intel.com/t5/Processors/Processor-Power-calculation/td-p/299459
        https://www.easycalculation.com/physics/electromagnetism/cpu-power-consumption.php

        """
        # Modify capacitive load based on processor documentation or existing models
        capacitive_load = 1 / 1000  # 1 micro farad
        capacitor_energy = self.capacitor_energy(capacitive_load, self.supply_voltage)

        # Increase the duration for better representation of the average activity factor
        duration = 5
        interval = 1

        with concurrent.futures.ThreadPoolExecutor() as executor:
            cpu = executor.map(self.activity_factor_cpu, [(process, interval, duration)])
        with concurrent.futures.ThreadPoolExecutor() as executor:
            gpu = executor.map(self.activity_factor_gpu, [(process, interval, duration)])

        activity_factor_cpu = list(cpu)[0]
        activity_factor_gpu = list(gpu)[0]

        dynamic_power = (capacitor_energy * (activity_factor_cpu + activity_factor_gpu))

        # Include static power estimation
        k = 1e-6  # Constant for static power, adjust according to processor technology. Ideally you would want to have this information as well
        temperature =  self.temperature + 273.15  # Assuming room temperature (in Kelvin)
        static_power = k * self.supply_voltage ** 2 * temperature

        # Total power is the sum of dynamic and static power
        total_power = dynamic_power + static_power

        return total_power * 60 * 60 

    def capacitor_energy(self, capacitance, voltage):
        return 0.5 * capacitance * voltage * voltage


    def activity_factor_cpu(self, tup):
        # The issue here is that the CPU activity unless it is a resource heavy application, is always 0 due to accuracy of the library

        process, interval, duration = tup[0], tup[1], tup[2]
        cpu_percentages = []

        process.cpu_percent(interval=None)

        for _ in range(int(duration / interval)):
            cpu_percent = process.cpu_percent(interval=interval)  
            cpu_percentages.append(cpu_percent)
            print("CPU percentage: ", cpu_percent)

        print("CPU percentage (list): ", cpu_percentages)
        cpu_percent_end = process.cpu_percent(interval=None)
        activity_factor = abs((cpu_percent_end - np.mean(cpu_percentages))) / 100.0
        print("CPU AF: ", activity_factor)
        return activity_factor


    def activity_factor_gpu(self, args):
        #Previous implementation was doing something similar to the CPu activity factor method.
        #However, there is no direct way to isolate process id in this library. On the other hand,
        #This library does give you overall GPU load normalised between 0-1

        # Another issue is that in linux, for some reason the library fails to detect GPU. It could simply just be an error
        # On my part in failing to set up my Virtual Machine properly. However, as it stands, i do not have a solution for this.
        gpu_list = GPUtil.getGPUs()
        print(gpu_list)
        if len(gpu_list) >0:
            for gpu in gpu_list:
                print(gpu)
                print(gpu.load)
                return gpu.load
            
        return 0.0


