import threading
import psutil
from Models import power_model
from View import power_view

class PowerController:
    def __init__(self):
        self.model = power_model.PowerModel()
        self.view = power_view.PowerView(self.calculate_power_consumption)

    def get_parent_processes(self):
        parent_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'ppid']):
            try:
                pinfo = proc.info
                if pinfo['name'] != 'System Idle Process' and pinfo['name'] != 'Idle':
                    if pinfo['ppid'] != 0 or proc.parent() is None:
                        # This is a main process
                        parent_processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return parent_processes
    
    def calculate_power_consumption(self, selected_process):
        self.view.loader_label.config(text="Calculating power consumption...")
        self.view.root.update()

        # Run the estimation on a separate thread
        estimation_thread = threading.Thread(target=self.run_estimation, args=(selected_process,))
        estimation_thread.start()


    def run_estimation(self, selected_process):
        power_consumption = self.model.estimate_power_consumption(selected_process['pid'])

        self.view.loader_label.config(text="")
        self.view.results_label.config(text=f"Estimated dynamic power consumption of {selected_process['name']}: {power_consumption:.10f} watts per hour")
    
    def run(self):
        self.model.get_system_info()
        processes = self.get_parent_processes()
        self.view.display_processes(processes)
        self.view.run()  # Start the tkinter main loop
