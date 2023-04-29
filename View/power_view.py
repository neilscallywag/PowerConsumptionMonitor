import tkinter as tk
from tkinter import ttk

class PowerView:
    def __init__(self, calculate_callback, root=None):
        self.root = root if root else tk.Tk()
        self.root.title("Power Consumption Estimator")
        self.calculate_callback = calculate_callback

        self.processes = []  
        self.index_to_pid = {}  
        self.create_widgets()

    def create_widgets(self):
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_processes_list)
        self.search_var.set("Search processes...")
        self.search_entry = ttk.Entry(self.root, textvariable=self.search_var)
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.search_entry.grid(column=0, row=0, sticky=(tk.W, tk.E), padx=(20, 10), pady=(10, 10))

        self.processes_list = tk.Listbox(self.root, height=15)
        self.processes_list.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.update_processes_list()


        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.processes_list.yview)
        self.processes_list.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(column=1, row=1, sticky=(tk.N, tk.S), padx=(0, 20), pady=(10, 10))

        self.calculate_button = ttk.Button(self.root, text="Calculate", command=self.calculate_power_consumption)
        self.calculate_button.grid(column=0, row=2, padx=(20, 10), pady=(10, 20), sticky="ew")

        self.loader_label = ttk.Label(self.root, text="")
        self.loader_label.grid(column=0, row=3, padx=10, pady=10, sticky="W")

        self.results_label = ttk.Label(self.root, text="")
        self.results_label.grid(column=0, row=4, padx=10, pady=10, sticky="W")
        # Make columns and rows expandable
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    def display_processes(self, processes):
        self.processes = processes
        self.update_processes_list()

    def update_processes_list(self, *args):
        if not hasattr(self, 'processes_list'):
            return
        search_term = self.search_var.get().lower()
        self.processes_list.delete(0, tk.END)
        self.index_to_pid.clear()  
        for index, proc in enumerate(self.processes):
            if search_term in proc['name'].lower():
                item = f"{proc['name']} ({proc['pid']})"
                self.processes_list.insert(tk.END, item)
                self.index_to_pid[self.processes_list.size() - 1] = proc['pid']  



    def calculate_power_consumption(self):
        selected_index = self.processes_list.curselection()
        if not selected_index:
            return

        selected_pid = self.index_to_pid[selected_index[0]]  # Get the process id from the index_to_pid mapping
        selected_process = next(proc for proc in self.processes if proc['pid'] == selected_pid)  # Find the process by its id

        self.loader_label.config(text="Calculating power consumption...")
        self.root.update()

        self.calculate_callback(selected_process)  # Use the calculate_callback



    def clear_search_placeholder(self, event=None):
        self.search_var.set("")
  
    def run(self):
        self.root.mainloop()