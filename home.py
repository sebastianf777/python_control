import PySimpleGUI as sg
import json
import os

class VariationTracker:
    def __init__(self, filename="data.json"):
        self.filename = filename
        self.principal_list = {
            'Group1': [{'Arg': 'String1', 'Variation1': 0, 'Variation2': 0}],
            'Group2': [{'Arg': 'String3', 'Variation1': 0, 'Variation2': 0}],
            'Group3': [{'Arg': 'String4', 'Variation1': 0, 'Variation2': 0}]
        }
        self.history = {group: [] for group in self.principal_list}
        self.load_data()

    def save_data(self):
        """Save the current state to a JSON file."""
        try:
            data = {
                'principal_list': self.principal_list,
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
                    # Validate structure
                    if 'principal_list' in data and 'history' in data:
                        self.principal_list = data['principal_list']
                        self.history = data['history']
                        print("Data loaded successfully!")
                    else:
                        print("Invalid data structure in file. Using defaults.")
            except json.JSONDecodeError:
                print("Error: File is not valid JSON. Using defaults.")
            except Exception as e:
                print(f"Error loading data: {e}")
        else:
            print("No saved data file found. Using defaults.")

    def add_argument(self, group, arg):
        if group in self.principal_list and not any(entry['Arg'] == arg for entry in self.principal_list[group]):
            self.principal_list[group].append({'Arg': arg, 'Variation1': 0, 'Variation2': 0})

    def remove_argument(self, group, arg):
        if group in self.principal_list:
            self.principal_list[group] = [entry for entry in self.principal_list[group] if entry['Arg'] != arg]

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
                        'NewValue': value
                    })
                    break

    def get_current_variations(self):
        return {group: [entry for entry in data] for group, data in self.principal_list.items()}

    def get_history(self, group):
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

    window = sg.Window('Variation Tracker', layout, finalize=True)

    def refresh_interface(selected_group=None):
        """Refresh the displayed data in the interface."""
        current_variations = "\n".join([
            f"{g}: {', '.join([f'{entry['Arg']} ({entry['Variation1']}, {entry['Variation2']})' for entry in v])}"
            for g, v in tracker.get_current_variations().items()
        ])
        window['-CURRENT-'].update(current_variations)

        if selected_group:
            args = [entry['Arg'] for entry in tracker.principal_list[selected_group]]
            window['-ARG-'].update(values=args)

            history = "\n".join([
                f"{h['Arg']} - {h['Variation']}: {h['OldValue']} -> {h['NewValue']}"
                for h in tracker.get_history(selected_group)
            ])
            window['-HISTORY-'].update(history)
        else:
            window['-ARG-'].update(values=[])
            window['-HISTORY-'].update("")

    # Initial refresh
    refresh_interface()

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            tracker.save_data()
            break

        group = values['-GROUP-']

        if event == '-GROUP-' and group:
            refresh_interface(selected_group=group)

        if event == 'Add Arg' and group:
            new_arg = values['-NEW_ARG-'].strip()
            if new_arg:
                tracker.add_argument(group, new_arg)
                refresh_interface(selected_group=group)
                window['-NEW_ARG-'].update('')

        if event == 'Remove Arg' and group:
            selected_arg = values['-ARG-']
            if selected_arg:
                tracker.remove_argument(group, selected_arg)
                refresh_interface(selected_group=group)

        if event == 'Update' and group:
            arg = values['-ARG-']
            variation = values['-VARIATION-']
            try:
                value = int(values['-VALUE-'])
                tracker.update_variation(group, arg, variation, value)
                refresh_interface(selected_group=group)
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
