import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os
from datetime import datetime


class VariationTracker:
    def __init__(self, filename="data.json"):
        self.filename = filename
        self.principal_list = {
            'Group1': [{'Arg': 'String1', 'Variation1': 0, 'Variation2': 0}],
            'Group2': [{'Arg': 'String1', 'Variation1': 0, 'Variation2': 0}],
            'Group3': [{'Arg': 'String1', 'Variation1': 0, 'Variation2': 0}]
        }
        self.global_arguments = ["String1"]  # Shared argument list for all groups
        self.history = {group: [] for group in self.principal_list}
        self.load_data()

    def save_data(self):
        try:
            data = {
                'principal_list': self.principal_list,
                'global_arguments': self.global_arguments,
                'history': self.history
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    if 'principal_list' in data and 'history' in data and 'global_arguments' in data:
                        self.principal_list = data['principal_list']
                        self.global_arguments = data['global_arguments']
                        self.history = data['history']
                        self.sync_arguments_with_groups()
            except Exception as e:
                print(f"Error loading data: {e}")

    def sync_arguments_with_groups(self):
        for group, entries in self.principal_list.items():
            for arg in self.global_arguments:
                if not any(entry['Arg'] == arg for entry in entries):
                    entries.append({'Arg': arg, 'Variation1': 0, 'Variation2': 0})

    def add_argument(self, arg):
        if arg not in self.global_arguments:
            self.global_arguments.append(arg)
            self.sync_arguments_with_groups()

    def remove_argument(self, arg):
        if arg in self.global_arguments:
            self.global_arguments.remove(arg)
            for group, entries in self.principal_list.items():
                self.principal_list[group] = [entry for entry in entries if entry['Arg'] != arg]

    def update_variation(self, group, arg, variation, value):
        if group in self.principal_list and variation in ['Variation1', 'Variation2']:
            for entry in self.principal_list[group]:
                if entry['Arg'] == arg:
                    old_value = entry[variation]
                    entry[variation] = value
                    self.history[group].append({
                        'Arg': arg,
                        'Variation': variation,
                        'OldValue': old_value,
                        'NewValue': value,
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    break

    def get_current_variations(self):
        return {group: data for group, data in self.principal_list.items()}

    def get_history(self, group):
        return self.history[group]


class VariationApp(tk.Tk):
    def __init__(self, tracker):
        super().__init__()
        self.title("Variation Tracker")
        self.geometry("800x600")
        self.tracker = tracker
        self.create_widgets()

    def create_widgets(self):
        # Dropdowns
        self.group_label = tk.Label(self, text="Group Selection")
        self.group_label.grid(row=0, column=0, padx=5, pady=5)
        self.group_combo = ttk.Combobox(self, values=["Group1", "Group2", "Group3"], state="readonly")
        self.group_combo.grid(row=0, column=1, padx=5, pady=5)
        self.group_combo.bind("<<ComboboxSelected>>", self.refresh_interface)

        self.arg_label = tk.Label(self, text="Argument Selection")
        self.arg_label.grid(row=1, column=0, padx=5, pady=5)
        self.arg_combo = ttk.Combobox(self, values=[], state="readonly")
        self.arg_combo.grid(row=1, column=1, padx=5, pady=5)

        self.var_label = tk.Label(self, text="Variation Selection")
        self.var_label.grid(row=2, column=0, padx=5, pady=5)
        self.var_combo = ttk.Combobox(self, values=["Variation1", "Variation2"], state="readonly")
        self.var_combo.grid(row=2, column=1, padx=5, pady=5)

        # New Argument Input
        self.new_arg_label = tk.Label(self, text="New Argument")
        self.new_arg_label.grid(row=3, column=0, padx=5, pady=5)
        self.new_arg_entry = tk.Entry(self)
        self.new_arg_entry.grid(row=3, column=1, padx=5, pady=5)

        # New Value Input
        self.new_value_label = tk.Label(self, text="New Value")
        self.new_value_label.grid(row=4, column=0, padx=5, pady=5)
        self.new_value_entry = tk.Entry(self)
        self.new_value_entry.grid(row=4, column=1, padx=5, pady=5)

        # Buttons
        self.add_arg_button = tk.Button(self, text="Add Arg", command=self.add_argument)
        self.add_arg_button.grid(row=3, column=2, padx=5, pady=5)
        self.remove_arg_button = tk.Button(self, text="Remove Arg", command=self.remove_argument)
        self.remove_arg_button.grid(row=3, column=3, padx=5, pady=5)
        self.update_button = tk.Button(self, text="Update", command=self.update_variation)
        self.update_button.grid(row=4, column=2, padx=5, pady=5)

        # Multiline Textboxes
        self.current_var_label = tk.Label(self, text="Current Variations:")
        self.current_var_label.grid(row=5, column=0, padx=5, pady=5)
        self.current_var_text = tk.Text(self, height=10, width=60)
        self.current_var_text.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

        self.history_label = tk.Label(self, text="History for Selected Group:")
        self.history_label.grid(row=6, column=0, padx=5, pady=5)
        self.history_text = tk.Text(self, height=10, width=60)
        self.history_text.grid(row=6, column=1, columnspan=2, padx=5, pady=5)

        # Keyboard Navigation for Combobox
        self.arg_combo.bind("<KeyRelease>", self.handle_key_navigation)

    def refresh_interface(self, event=None):
        group = self.group_combo.get()
        if group:
            args = [entry["Arg"] for entry in self.tracker.principal_list[group]]
            self.arg_combo["values"] = args
            self.current_var_text.delete(1.0, tk.END)
            variations = self.tracker.get_current_variations()
            for g, entries in variations.items():
                self.current_var_text.insert(tk.END, f"{g}: {entries}\n")
            self.history_text.delete(1.0, tk.END)
            history = self.tracker.get_history(group)
            for entry in history:
                self.history_text.insert(
                    tk.END, f"{entry['Arg']} - {entry['Variation']}: {entry['OldValue']} -> {entry['NewValue']} ({entry['Timestamp']})\n"
                )

    def handle_key_navigation(self, event):
        """Allow selecting items by typing the first letter."""
        if event.widget == self.arg_combo:
            typed_char = event.char.lower()
            current_values = self.arg_combo["values"]
            matching_value = next((value for value in current_values if value.lower().startswith(typed_char)), None)
            if matching_value:
                self.arg_combo.set(matching_value)

    def add_argument(self):
        new_arg = self.new_arg_entry.get()
        if new_arg:
            self.tracker.add_argument(new_arg)
            self.refresh_interface()

    def remove_argument(self):
        selected_arg = self.arg_combo.get()
        if selected_arg:
            self.tracker.remove_argument(selected_arg)
            self.refresh_interface()
    def update_variation(self):
        group = self.group_combo.get()
        arg = self.arg_combo.get()
        variation = self.var_combo.get()
        try:
            value = int(self.new_value_entry.get())  # Get the new value from the input field
            self.tracker.update_variation(group, arg, variation, value)  # Update the tracker
            self.refresh_interface()  # Refresh the displayed data
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer value for the new value.")  # Error handling

    def refresh_interface(self, event=None):
        """Refresh the interface components based on the selected group."""
        group = self.group_combo.get()
        if group:
            args = [entry["Arg"] for entry in self.tracker.principal_list[group]]
            self.arg_combo["values"] = args  # Update the argument dropdown with the current group's arguments
            self.current_var_text.delete(1.0, tk.END)
            variations = self.tracker.get_current_variations()
            for g, entries in variations.items():
                # Display current variations in the text area
                self.current_var_text.insert(tk.END, f"{g}: {entries}\n")
            self.history_text.delete(1.0, tk.END)
            history = self.tracker.get_history(group)
            for entry in history:
                # Display the history for the selected group
                self.history_text.insert(
                    tk.END,
                    f"{entry['Arg']} - {entry['Variation']}: {entry['OldValue']} -> {entry['NewValue']} ({entry['Timestamp']})\n"
                )

    def handle_key_navigation(self, event):
        """Allow keyboard navigation in the argument combobox."""
        if event.widget == self.arg_combo:
            typed_char = event.char.lower()
            current_values = self.arg_combo["values"]
            matching_value = next((value for value in current_values if value.lower().startswith(typed_char)), None)
            if matching_value:
                self.arg_combo.set(matching_value)  # Set the combobox value to the matching one


if __name__ == "__main__":
    tracker = VariationTracker()  # Initialize the tracker
    app = VariationApp(tracker)  # Initialize the app
    app.mainloop()  # Run the main loop
