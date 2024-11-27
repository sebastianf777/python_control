import PySimpleGUI as sg
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
        """Save the current state to a JSON file."""
        try:
            data = {
                'principal_list': self.principal_list,
                'global_arguments': self.global_arguments,
                'history': self.history
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
            print("Data saved successfully!")
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        """Load state from a JSON file if it exists."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    if 'principal_list' in data and 'history' in data and 'global_arguments' in data:
                        self.principal_list = data['principal_list']
                        self.global_arguments = data['global_arguments']
                        self.history = data['history']

                        # Ensure all global arguments exist in each group
                        self.sync_arguments_with_groups()

                        print("Data loaded successfully!")
                    else:
                        print("Invalid data structure in file. Using defaults.")
            except json.JSONDecodeError:
                print("Error: File is not valid JSON. Using defaults.")
            except Exception as e:
                print(f"Error loading data: {e}")
        else:
            print("No saved data file found. Using defaults.")

    def sync_arguments_with_groups(self):
        """Ensure all global arguments exist in every group's principal_list."""
        for group, entries in self.principal_list.items():
            for arg in self.global_arguments:
                if not any(entry['Arg'] == arg for entry in entries):
                    entries.append({'Arg': arg, 'Variation1': 0, 'Variation2': 0})

    def add_argument(self, arg):
        """Add a global argument and update each group's principal_list."""
        if arg not in self.global_arguments:
            self.global_arguments.append(arg)
            self.sync_arguments_with_groups()

    def remove_argument(self, arg):
        """Remove a global argument and update each group's principal_list."""
        if arg in self.global_arguments:
            self.global_arguments.remove(arg)
            for group, entries in self.principal_list.items():
                self.principal_list[group] = [entry for entry in entries if entry['Arg'] != arg]

    def update_variation(self, group, arg, variation, value):
        """Update a specific variation for an argument in a group."""
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
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add timestamp
                    })
                    break

    def get_current_variations(self):
        """Get all current variations."""
        return {group: data for group, data in self.principal_list.items()}

    def get_history(self, group):
        """Get the history of updates for a group."""
        return self.history[group]


def main():
    tracker = VariationTracker()

    layout = [
        [sg.Text('Group Selection'), sg.Combo(['Group1', 'Group2', 'Group3'], key='-GROUP-', readonly=True, enable_events=True)],
        [sg.Text('Argument Selection'), sg.Combo([], key='-ARG-', readonly=True)],
        [sg.Text('New Argument'), sg.InputText(key='-NEW_ARG-'), sg.Button('Add Arg'), sg.Button('Remove Arg')],
        [sg.Text('Variation Selection'), sg.Combo(['Variation1', 'Variation2'], key='-VARIATION-', readonly=True)],
        [sg.Text('New Value'), sg.InputText(key='-VALUE-'), sg.Button('Update')],
        [sg.Button('Save Data'), sg.Button('Load Data')],
        [sg.Text('Current Variations:'), sg.Multiline(size=(60, 10), key='-CURRENT-', disabled=True)],
        [sg.Text('History for Selected Group:'), sg.Multiline(size=(60, 10), key='-HISTORY-', disabled=True)]
    ]
    # Enable tabbing and keyboard focus for the ComboBoxes
    window = sg.Window('Variation Tracker', layout, finalize=True)

    def refresh_interface(selected_group=None, selected_argument=None):
        """Refresh the displayed data in the interface."""
        # Refresh current variations
        current_variations = "\n".join([
            f"{g}: {', '.join([f'{entry['Arg']} ({entry['Variation1']}, {entry['Variation2']})' for entry in v])}"
            for g, v in tracker.get_current_variations().items()
        ])
        window['-CURRENT-'].update(current_variations)

        # Update argument list (shared across all groups)
        window['-ARG-'].update(values=tracker.global_arguments)

        # Retain the last selected argument
        if selected_argument:
            window['-ARG-'].update(value=selected_argument)

        # Refresh history if a group is selected
        if selected_group:
            history = "\n".join([
                f"{h['Arg']} - {h['Variation']}: {h['OldValue']} -> {h['NewValue']} at {h['Timestamp']}"
                for h in tracker.get_history(selected_group)
            ])
            window['-HISTORY-'].update(history)
        else:
            window['-HISTORY-'].update("")

    # Initial refresh
    refresh_interface()
    
    
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            tracker.save_data()
            break

        if event == 'Add Arg':
            new_arg = values['-NEW_ARG-'].strip()
            if new_arg:
                tracker.add_argument(new_arg)
                refresh_interface()
                window['-NEW_ARG-'].update('')

        if event == 'Remove Arg':
            selected_arg = values['-ARG-']
            if selected_arg:
                tracker.remove_argument(selected_arg)
                refresh_interface()

        if event == 'Update':
            group = values['-GROUP-']
            arg = values['-ARG-']
            variation = values['-VARIATION-']
            try:
                value = int(values['-VALUE-'])
                tracker.update_variation(group, arg, variation, value)
                refresh_interface(selected_group=group, selected_argument=arg)
            except ValueError:
                sg.popup('Please enter a valid integer for the value.')

        if event == 'Save Data':
            tracker.save_data()
            sg.popup('Data saved successfully!')

        if event == 'Load Data':
            tracker.load_data()
            refresh_interface()
            sg.popup('Data loaded successfully!')

    window.close()


if __name__ == "__main__":
    main()
