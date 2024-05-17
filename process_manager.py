import psutil
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time

# Function to set priority
def set_priority(process, priority):
    try:
        old_priority = process.nice() if hasattr(process, 'nice') else psutil.Process(process.pid).nice()
        process.nice(priority)
        print(f"Priority of process with PID {process.pid} has been changed from {old_priority} to {priority}.")
        return True
    except psutil.AccessDenied:
        print(f"Access denied. You don't have permission to modify the priority of this process.")
    except Exception as e:
        print("Error:", e)
    return False

# Function to refresh process list
def refresh_processes():
    show_loading_screen()
    def refresh_task():
        global filtered_processes
        process_list.delete(0, tk.END)
        for proc in filtered_processes:
            process_list.insert(tk.END, f"PID: {proc.info['pid']} | Name: {proc.info['name']} | Username: {proc.info['username']} | Status: {proc.info['status']} | Nice Value: {proc.info['nice']} | CPU Percent: {proc.info['cpu_percent']}")
            process_list.insert(tk.END, "")  # Add an empty line for spacing
        close_loading_screen()
    
    thread = Thread(target=refresh_task)
    thread.start()

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
        except ValueError:
            print("Invalid input. Please enter a valid process ID.")
        except Exception as e:
            print(f"Error when trying to modify priority of process with PID {selected_pid}: {e}")

# Function to restore all processes to their normal priorities
def restore_normal_priorities():
    show_loading_screen()
    def restore_task():
        for proc in psutil.process_iter():
            try:
                proc.nice(psutil.NORMAL_PRIORITY_CLASS)
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"Error while restoring priority for process with PID {proc.pid}: {e}")
        refresh_processes()
        close_loading_screen()
    
    thread = Thread(target=restore_task)
    thread.start()

# Function to perform search by process name
def perform_search():
    show_loading_screen()
    def search_task():
        search_query = search_entry.get().strip()
        global filtered_processes
        if search_query:
            filtered_processes = [proc for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'nice', 'cpu_percent']) if search_query.lower() in proc.info['name'].lower()]
        else:
            filtered_processes = psutil.process_iter(['pid', 'name', 'username', 'status', 'nice', 'cpu_percent'])
        refresh_processes()
        close_loading_screen()
    
    thread = Thread(target=search_task)
    thread.start()

# Function to show loading screen
def show_loading_screen():
    global loading_screen
    loading_screen = tk.Toplevel(root)
    loading_screen.title("Loading")
    tk.Label(loading_screen, text="Please wait, loading...").pack(padx=20, pady=20)
    loading_screen.geometry("200x100")
    loading_screen.transient(root)
    loading_screen.grab_set()

# Function to close loading screen
def close_loading_screen():
    loading_screen.grab_release()
    loading_screen.destroy()

# Create main window
root = tk.Tk()
root.title("Process Priority Adjuster")

# Create process list
process_frame = tk.Frame(root)
process_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

tk.Label(process_frame, text="Processes:").pack()
process_list = tk.Listbox(process_frame, selectmode=tk.SINGLE, width=100, height=20)
process_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add scroll wheel
scrollbar = tk.Scrollbar(process_frame, orient=tk.VERTICAL, command=process_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
process_list.config(yscrollcommand=scrollbar.set)

# Create search entry
search_frame = tk.Frame(root)
search_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame, width=50)
search_entry.pack(side=tk.LEFT)
tk.Button(search_frame, text="Search", command=perform_search).pack(side=tk.LEFT)

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

tk.Button(button_frame, text="Refresh", command=refresh_processes).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Change Priority", command=change_priority).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Restore Normal Priorities", command=restore_normal_priorities).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Exit", command=root.destroy).pack(side=tk.LEFT, padx=5)

# Initial process list refresh
filtered_processes = psutil.process_iter(['pid', 'name', 'username', 'status', 'nice', 'cpu_percent'])
refresh_processes()

# Run the application
root.mainloop()
