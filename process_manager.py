import psutil
import tkinter as tk
from ctypes import windll, c_uint

# Function to set priority
def set_priority(process, priority):
    try:
        old_priority = process.nice() if hasattr(process, 'nice') else windll.kernel32.GetPriorityClass(process.pid)
        
        if hasattr(process, 'nice'):  # For Unix-based systems
            process.nice(priority)
        else:  # For Windows-based systems
            windll.kernel32.SetPriorityClass(process.pid, c_uint(priority))
        
        print(f"Priority of process with PID {process.pid} has been changed from {old_priority} to {priority}.")
        return True
    except Exception as e:
        print("Error:", e)
        return False

# Function to refresh process list
def refresh_processes():
    process_list.delete(0, tk.END)
    for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'nice', 'cpu_percent']):
        process_list.insert(tk.END, f"PID: {proc.info['pid']} | Name: {proc.info['name']} | Username: {proc.info['username']} | Status: {proc.info['status']} | Nice Value: {proc.info['nice']} | CPU Percent: {proc.info['cpu_percent']}")

# Function to change priority
def change_priority():
    selected_index = process_list.curselection()
    if selected_index:
        selected_pid = int(process_list.get(selected_index[0]).split()[1])
        priority = priority_var.get()
        try:
            process = psutil.Process(selected_pid)
            if set_priority(process, priority):
                refresh_processes()
        except psutil.NoSuchProcess:
            print(f"Process with PID {selected_pid} no longer exists.")
        except psutil.AccessDenied:
            print(f"Access denied when trying to modify priority of process with PID {selected_pid}.")
        except Exception as e:
            print(f"Error when trying to modify priority of process with PID {selected_pid}: {e}")

# Function to sort processes by highest to lowest priority
def sort_by_highest_priority():
    process_list.delete(0, tk.END)
    sorted_processes = sorted((proc for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'nice', 'cpu_percent']) if proc.info['nice'] is not None), key=lambda x: x.info['nice'], reverse=True)
    for proc in sorted_processes:
        process_list.insert(tk.END, f"PID: {proc.info['pid']} | Name: {proc.info['name']} | Username: {proc.info['username']} | Status: {proc.info['status']} | Nice Value: {proc.info['nice']} | CPU Percent: {proc.info['cpu_percent']}")

# Function to sort processes by lowest to highest priority
def sort_by_lowest_priority():
    process_list.delete(0, tk.END)
    sorted_processes = sorted((proc for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'nice', 'cpu_percent']) if proc.info['nice'] is not None), key=lambda x: x.info['nice'])
    for proc in sorted_processes:
        process_list.insert(tk.END, f"PID: {proc.info['pid']} | Name: {proc.info['name']} | Username: {proc.info['username']} | Status: {proc.info['status']} | Nice Value: {proc.info['nice']} | CPU Percent: {proc.info['cpu_percent']}")
# Function to restore all processes to their normal priorities
# Function to restore all processes to their normal priorities
# Function to restore all processes to their normal priorities
def restore_normal_priorities():
    for proc in psutil.process_iter():
        try:
            if hasattr(proc, 'nice'):
                if proc.nice() != psutil.NORMAL_PRIORITY_CLASS:
                    proc.nice(psutil.NORMAL_PRIORITY_CLASS)   
            else:
                current_priority = windll.kernel32.GetPriorityClass(proc.pid)
                if current_priority != psutil.NORMAL_PRIORITY_CLASS:
                    windll.kernel32.SetPriorityClass(proc.pid, psutil.NORMAL_PRIORITY_CLASS)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error while restoring priority for process with PID {proc.pid}: {e}")
    refresh_processes()


# Create main window
root = tk.Tk()
root.title("Process Priority Adjuster")

# Create process list
process_frame = tk.Frame(root)
process_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

tk.Label(process_frame, text="Processes:").pack()
process_list = tk.Listbox(process_frame, selectmode=tk.SINGLE)
process_list.pack(fill=tk.BOTH, expand=True)

# Create priority selector
priority_frame = tk.Frame(root)
priority_frame.pack(padx=10, pady=10)

tk.Label(priority_frame, text="Priority:").pack(side=tk.LEFT)
priority_var = tk.IntVar(priority_frame)
priority_var.set(psutil.NORMAL_PRIORITY_CLASS)

priority_options = [
    (psutil.ABOVE_NORMAL_PRIORITY_CLASS, "Above Normal"),
    (psutil.BELOW_NORMAL_PRIORITY_CLASS, "Below Normal"),
    (psutil.HIGH_PRIORITY_CLASS, "High"),
    (psutil.IDLE_PRIORITY_CLASS, "Idle"),
    (psutil.NORMAL_PRIORITY_CLASS, "Normal"),
    (psutil.REALTIME_PRIORITY_CLASS, "Realtime")
]

for priority, text in priority_options:
    tk.Radiobutton(priority_frame, text=text, variable=priority_var, value=priority).pack(side=tk.LEFT)

# Create buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Refresh", command=refresh_processes).pack(side=tk.LEFT)
tk.Button(button_frame, text="Change Priority", command=change_priority).pack(side=tk.LEFT)
tk.Button(button_frame, text="Sort by Highest Priority", command=sort_by_highest_priority).pack(side=tk.LEFT)
tk.Button(button_frame, text="Sort by Lowest Priority", command=sort_by_lowest_priority).pack(side=tk.LEFT)
tk.Button(button_frame, text="Restore Normal Priorities", command=restore_normal_priorities).pack(side=tk.LEFT)
tk.Button(button_frame, text="Exit", command=root.destroy).pack(side=tk.LEFT)

# Initial process list refresh
refresh_processes()

# Run the application
root.mainloop()
