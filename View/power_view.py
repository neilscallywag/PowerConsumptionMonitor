
class PowerView:
    def __init__(self):
        pass

    def display_processes(self, processes):
        print("Select a process:")
        for i, proc in enumerate(processes):
            print(f"{i+1}. {proc['name']} ({proc['pid']})")

    def get_user_selection(self):
        return int(input("Enter the process number: "))

    def display_power_consumption(self, process_name, power_consumption):
        print(f"Estimated dynamic power consumption of the {process_name}: {power_consumption:.10f} watts")
