# PEP8 Compliant Guidance
# Standard Library Imports
import logging
import threading

# Third-Party Library Imports

# Local Application/Library Specific Imports
from functions.json_functions import load_hours_data_from_json

class WorkbookDataLoader(threading.Thread):
    def __init__(self, schedule_hrs_frame):
        super().__init__()
        self.schedule_hrs_frame = schedule_hrs_frame

    def run(self):
        try:
            crew = self.schedule_hrs_frame.user_selections['selected_crew']
            month = self.schedule_hrs_frame.user_selections['selected_month'].month
            year = self.schedule_hrs_frame.user_selections['selected_year'].year
            schedule_type = self.schedule_hrs_frame.schedule_type

            print(f"Loading data for crew: {crew}, month: {month}, year: {year}, schedule_type: {schedule_type}")
            data = load_hours_data_from_json(crew, month, year, schedule_type)
            print(f"Data loaded. Number of crew members: {len(data)}")

            self.schedule_hrs_frame.after(0, self.schedule_hrs_frame.data_loaded, data, None)
        except Exception as e:
            print(f"An error occurred while loading JSON data: {str(e)}")
            self.schedule_hrs_frame.after(0, self.schedule_hrs_frame.data_loaded, None, e)