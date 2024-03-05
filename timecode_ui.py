# timecode_ui.py - User interface to allow users to record time against specific projects and activities.
# github.com/vh3/timecoder - code generated with chatchpt4, tested on macos

import tkinter as tk
from tkinter import ttk, messagebox
import getpass
import uuid
from datetime import datetime, timedelta
import json
import os
import csv
import platform

"""
Change Log:
Version 1.0 - Initial version with basic functionality
Version 1.1 - Added dynamic project/task dropdowns
Version 1.2 - Introduced bilingual interface
Version 1.3 - Accessibility features added
Version 1.4 - Timer functionality improved
Version 1.5 - Fixed dynamic "PE" value display
Version 1.6 - Ensured "EN" output consistency
Version 1.7 - Corrected language toggle behavior
Version 1.8 - Added version tracking comment block
Version 1.9 - Fixed identifier label & timer updates
Version 2.0 - Output file now uses "EN" values
Version 2.1 - Added a keybinding for Ctrl-t to the start/stop toggle on windows and Command-t for macos
"""

def get_current_user_id():
    """Retrieve the currently logged-in user, cross-platform."""
    return getpass.getuser()

def load_input_parameters(file_path="timecode_parameters.json"):
    """Load tasks and projects from a JSON file."""
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

class ProjectCoderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.data = load_input_parameters()
        self.userid = get_current_user_id()
        self.current_language = "EN"  # Default language
        self.timer_start = None
        self.timer_running = False
        self.unique_identifier = uuid.uuid4().hex[:16]
        self.selected_project_Code = "0000"  # Default Code value
        self.initialize_ui()
        self.toggle_language(initial=True)

    def initialize_ui(self):
        # self.title("Project Coder")
        self.geometry("")  # Auto-size
        self.resizable(True, True)
        self.attributes("-topmost", True)

        # Project Dropdown
        self.project_label = ttk.Label(self, text="")
        self.project_label.pack(side=tk.LEFT)
        self.project_var = tk.StringVar()
        self.project_dropdown = ttk.Combobox(self, textvariable=self.project_var, state="readonly")
        self.project_dropdown.pack(side=tk.LEFT)
        self.project_dropdown.bind("<<ComboboxSelected>>", self.on_project_change)

        # Task Dropdown
        self.task_label = ttk.Label(self, text="")
        self.task_label.pack(side=tk.LEFT)
        self.task_var = tk.StringVar()
        self.task_dropdown = ttk.Combobox(self, textvariable=self.task_var, state="readonly")
        self.task_dropdown.pack(side=tk.LEFT)

        # User Entered Identifier
        self.user_identifier_label = ttk.Label(self, text="Identifier")
        self.user_identifier_label.pack(side=tk.LEFT)
        self.user_identifier_entry = ttk.Entry(self)
        self.user_identifier_entry.pack(side=tk.LEFT)

        # Timer Display
        self.timer_display = ttk.Label(self, text="00:00:00")
        self.timer_display.pack(side=tk.LEFT)

        # Start/Stop Button
        self.start_stop_button = ttk.Button(self, text="Start", command=self.toggle_timer)
        self.start_stop_button.pack(side=tk.LEFT, padx=5)

        # Language Toggle Button
        self.language_button = ttk.Button(self, text="", command=lambda: self.toggle_language(initial=False))
        self.language_button.pack(side=tk.RIGHT, padx=5)

        # Styling for Start/Stop Button
        self.style = ttk.Style(self)
        self.style.configure("Start.TButton", foreground="green", font=('Helvetica', 12))
        self.style.configure("Stop.TButton", foreground="red", font=('Helvetica', 12))

        # Define a key binding for 'Ctrl+T' to toggle the timer
        # Adjust key binding for macOS compatibility
        if platform.system() == "Darwin":  # Darwin is the system name for macOS
            self.bind_all("<Command-t>", self.toggle_timer_event)  # Use Command key on macOS
        else:
            self.bind_all("<Control-t>", self.toggle_timer_event)  # Use Control key on other OSes

    def populate_dropdowns(self):
        project_names = [info[self.current_language] for info in self.data["projects"].values()]
        self.project_dropdown['values'] = project_names
        self.project_dropdown.set('')  # Clear project dropdown initially
        self.task_dropdown.set('')  # Clear task dropdown initially

    def on_project_change(self, event=None):
        project_key = list(self.data["projects"].keys())[self.project_dropdown.current()]
        selected_project = self.data["projects"][project_key]
        tasks_for_project = selected_project["tasks"]
        self.task_dropdown['values'] = [self.data["tasks"][task][self.current_language] for task in tasks_for_project]

        # Reset the value of the task field
        self.task_var.set('')

        self.selected_project_Code = selected_project["Code"]  # Update Code value for the selected project
        self.user_identifier_entry.delete(0, tk.END)  # Clear the identifier entry field

        # Update the identifier label with the selected project's identifier
        identifier_text = selected_project.get("identifier", "Identifier")  # Default to "Identifier" if not found
        self.user_identifier_label.config(text=identifier_text)

    def toggle_language(self, initial):
        if self.timer_running and not initial:
            messagebox.showwarning("Warning", "Cannot change language while timer is running.")
            return
        if not initial:
            self.current_language = "FR" if self.current_language == "EN" else "EN"
        self.update_ui_texts()
        self.populate_dropdowns()

    def update_ui_texts(self):
        
        translations = {
            "EN": {"title": "Project Coder", "project": "Project", "task": "Task", "start": "Start", "stop": "Stop", "language_toggle": "FR", "identifier": "Identifier"},
            "FR": {"title": "Codeur de Projet", "project": "Projet", "task": "Tâche", "start": "Démarrer", "stop": "Arrêter", "language_toggle": "EN", "identifier": "Identifiant"}
        }
        lang = translations[self.current_language]
        self.title(lang["title"])  # Update window title based on current language
        self.project_label.config(text=lang["project"])
        self.task_label.config(text=lang["task"])

        # TODO: fix the identifier reverting to the default
        # Update the identifier label - need to get the value from the table
        # self.user_identifier_label.config(text=lang["identifier"])

        self.start_stop_button.config(text=lang["start"] if not self.timer_running else lang["stop"])
        self.language_button.config(text=lang["language_toggle"])
        
        # TODO: this function is called when the start/stop timer is toggled also.  We don't want to delete the identifier when we run the timer.  Fix this later
        # self.user_identifier_entry.delete(0, tk.END)  # Clear the identifier entry field on language toggle

    def toggle_timer_event(self, event=None):
        """Event handler to toggle the timer with a keyboard shortcut."""
        self.toggle_timer()

    def toggle_timer(self):
        if not self.project_dropdown.get() or not self.task_dropdown.get():
            messagebox.showerror("Error", "Both project and task must be selected.")
            return
        self.timer_running = not self.timer_running
        if self.timer_running:
            self.timer_start = datetime.now()
            self.start_stop_button.config(text="Stop", style="Stop.TButton")
            self.update_timer()
        else:
            self.output_time_record()
            self.start_stop_button.config(text="Start", style="Start.TButton")
            self.timer_start = None  # Reset timer start
            
            # Reset the timer to 00:00:00
            self.timer_display.config(text=str("00:00:00").split('.')[0])
            self.update_timer()

        self.update_ui_texts()  # Ensure UI texts, including button labels, are updated based on current language

    def update_timer(self):
        """Update the timer display while the timer is running."""
        if self.timer_running:
            elapsed_time = datetime.now() - self.timer_start
            self.timer_display.config(text=str(elapsed_time).split('.')[0])  # Update display without microseconds
            self.after(1000, self.update_timer)  # Schedule next update

    def output_time_record(self):
        output_folder = f"/Users/{self.userid}/Documents"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)  # Ensure the directory exists
        output_filename = f"timecode.{self.unique_identifier}.csv"
        output_path = os.path.join(output_folder, output_filename)
        datetime_format = "%Y-%m-%d %H:%M:%S"
        datetime_start = self.timer_start.strftime(datetime_format)
        datetime_end = datetime.now().strftime(datetime_format)
        
        # Fetch English versions for project and task
        selected_project_index = self.project_dropdown.current()
        selected_project_key = list(self.data["projects"].keys())[selected_project_index]
        project_en = self.data["projects"][selected_project_key]["EN"]  # English name of the project
        
        selected_task = self.task_var.get()
        task_en = None
        for task_key, task_value in self.data["tasks"].items():
            if task_value[self.current_language] == selected_task:
                task_en = task_value["EN"]  # English name of the task
                break

        user_entered_identifier = self.user_identifier_entry.get()
        Code = self.selected_project_Code  # Code value for the selected project

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['userid', 'datetime_start', 'datetime_end', 'project', 'user_entered_identifier', 'task', 'Code']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                'userid': self.userid,
                'datetime_start': datetime_start,
                'datetime_end': datetime_end,
                'project': project_en,  # Use English version
                'user_entered_identifier': user_entered_identifier,
                'task': task_en,  # Use English version
                'Code': Code
            })

        # Remove the message box for production!
        messagebox.showinfo("Success", f"Time record saved to {output_path}.")

if __name__ == "__main__":
    app = ProjectCoderApp()
    app.mainloop()
