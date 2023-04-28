import psutil
from Models import power_model
from View import power_view

class PowerController:
    def __init__(self):
        self.model = power_model.PowerModel()
        self.view = power_view.PowerView()

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
    
    def run(self):
        self.model.get_system_info()
        processes = self.get_parent_processes()
        endcon = False
        self.view.display_processes(processes)
        selection = self.view.get_user_selection()
        while not endcon:
            if selection == 00000:
                endcon = True
            pid = processes[selection-1]['pid']
            try:
                power_consumption = self.model.estimate_power_consumption(pid)
                process_name = processes[selection-1]['name']
                self.view.display_power_consumption(process_name, power_consumption)
                selection = self.view.get_user_selection()
            except psutil.NoSuchProcess:
                print("Invalid process selected. Please select a valid process.")
                continue