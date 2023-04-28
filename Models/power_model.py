import concurrent.futures
import numpy as np
import psutil
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
            self.clock_frequency =windows_utils. get_clock_frequency()
            self.supply_voltage = windows_utils.get_supply_voltage()
        elif platform.system() == 'Linux':
            from Utils import linux_utils
            self.clock_frequency = linux_utils.get_clock_frequency()
            self.supply_voltage = linux_utils.get_supply_voltage()
        else:
            raise Exception("Unsupported operating system")
    

    def estimate_power_consumption(self, pid):
        """
        Ideally you would want to estimate the power consumption using CPU Utilisation * CPU thermal Design Power
        Where TDP is given by CPU TDP and GPU TDP. However, there is no straightforward way to estimate or calculate that. 


        Instead we are going to use indirect measures to calculate using the standard Power Formula. 

        Power Consumption formula here only considers dynamic power. 
        https://semiengineering.com/knowledge_centers/low-power/low-power-design/power-consumption/
        """        
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        processes= [parent] + children
        print(processes)
                # Create a multiprocessing pool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.estimate_power_for_process, processes)

        dynamic_power = sum(results)
        return dynamic_power

        # To do: Calculate not just for this process but all its children as well

    def estimate_power_for_process(self, process):
        capacitive_load = 1/1000 #1 micro farad
        capacitor_energy = self.capacitor_energy(capacitive_load,self.supply_voltage)
        activity_factor = self.activity_factor(process, 0.1, 5)
        dynamic_power = capacitor_energy * activity_factor
        return dynamic_power
    
    
    def capacitor_energy(self,capacitance, voltage):
        return 0.5*capacitance*voltage*voltage

    def activity_factor(self,process, interval, duration):
        # Current challenge of using this is that if the CPU utilisation is very low, it gives 0.0% utilisation
        cpu_percentages = []
        for _ in range(int(duration / interval)):
            cpu_percentages.append(process.cpu_percent(interval=interval))
            time.sleep(interval)
        cpu_percent_end = process.cpu_percent(interval=None)
        activity_factor = abs((cpu_percent_end - np.mean(cpu_percentages))) / 100.0
        return activity_factor
    
