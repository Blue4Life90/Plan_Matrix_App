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
            
            #TODO: Remove if not needed
            #create_hours_data_json(crew, year, schedule_type)

            data = load_hours_data_from_json(crew, month, year, schedule_type)

            self.schedule_hrs_frame.after(0, self.schedule_hrs_frame.data_loaded, data, None)
        except Exception as e:
            logging.error("An error occurred while loading JSON data.")
            logging.exception(f"WorkbookDataLoader.run: Exception:{str(e)}")
            self.schedule_hrs_frame.after(0, self.schedule_hrs_frame.data_loaded, None, e)