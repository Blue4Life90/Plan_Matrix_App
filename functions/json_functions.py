# PEP8 Compliant Guidance
# Standard Library Imports
import os
import json
import logging

# Third-Party Library Imports

# Local Application/Library Specific Imports
from constants import log_file
from PathConfig import get_shared_path
from CrewMemberHours import CrewMemberHours

# Logging Format
logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file, 
                    filemode='a'
)

class DataCache:
    def __init__(self):
        self.cache = {}
        self.last_load_time = {}

    def get_data(self, crew, month, year, schedule_type):
        if schedule_type == "Overtime":
            schedule_prefix = "OT"
        else:
            schedule_prefix = "WS"
        
        cache_key = f"{schedule_prefix}_{crew}_{year}"
        shared_path = get_shared_path() or os.getcwd()
        json_filepath = os.path.join(shared_path, "SaveFiles", f"{schedule_prefix}_{crew}_{year}.json")
        
        if not os.path.exists(json_filepath):
            create_hours_data_json(crew, year, "Overtime")
            create_hours_data_json(crew, year, "work_schedule")
        
        if cache_key not in self.cache or self.is_file_modified(json_filepath, cache_key):
            with open(json_filepath, 'r') as file:
                self.cache[cache_key] = json.load(file)
                self.last_load_time[cache_key] = self.get_file_modification_time(json_filepath)

        month_data = self.cache[cache_key].get("month", {}).get(str(month), {})
        return month_data

    def is_file_modified(self, json_filepath, cache_key):
        current_modification_time = self.get_file_modification_time(json_filepath)
        last_modification_time = self.last_load_time.get(cache_key)
        return current_modification_time != last_modification_time

    @staticmethod
    def get_file_modification_time(file_path):
        if os.path.exists(file_path):
            return os.path.getmtime(file_path)
        return None

data_cache = DataCache()

def create_hours_data_json(crew, year, schedule_type):
    shared_path = get_shared_path() or os.getcwd()
    save_folder = os.path.join(shared_path, "SaveFiles")
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        
    if schedule_type == "Overtime":
        schedule_prefix = "OT"
    else:
        schedule_prefix = "WS"

    json_filename = f"{schedule_prefix}_{crew}_{year}.json"
    json_filepath = os.path.join(save_folder, json_filename)

    if not os.path.exists(json_filepath):
        
        if schedule_prefix == "OT":
            prev_year = year - 1
            prev_year_json_filepath = f"{schedule_prefix}_{crew}_{prev_year}.json"
            prev_year_json_filepath = os.path.join(save_folder, prev_year_json_filepath)
            if os.path.exists(prev_year_json_filepath):
                prev_year_data = load_hours_data_from_json(crew, 12, prev_year, schedule_type)
            else:
                prev_year_data = None

            if prev_year_data:
                # Previous year's data exists, create new year's data based on rankings
                ranking_data = [(name, member.monthly_hours['total_working_hours'], member.monthly_hours['total_asking_hours'])
                                for name, member in prev_year_data.items()]
                ranking_data.sort(key=lambda x: x[1])
                working_hours_ranks = {name: rank for rank, (name, _, _) in enumerate(ranking_data)}
                ranking_data.sort(key=lambda x: x[2])
                asking_hours_ranks = {name: rank for rank, (name, _, _) in enumerate(ranking_data)}

                new_year_data = {
                    "month": {
                        str(month): {
                            name: {
                                "monthly_hours": {
                                    "starting_asking_hours": asking_hours_ranks[name],
                                    "starting_working_hours": working_hours_ranks[name],
                                    "total_asking_hours": asking_hours_ranks[name],
                                    "total_working_hours": working_hours_ranks[name],
                                    "asking_hours_data": [],
                                    "working_hours_data": []
                                }
                            } for name in prev_year_data.keys()
                        } for month in range(1, 13)
                    }
                }
            
            else:
                # If no previous year's data, create template data
                new_year_data = {
                    "month": {
                        str(month): {
                            "[placeholder]": {
                                "monthly_hours": {
                                    "starting_asking_hours": 0,
                                    "starting_working_hours": 0,
                                    "total_asking_hours": 0,
                                    "total_working_hours": 0,
                                    "asking_hours_data": [],
                                    "working_hours_data": []
                                }
                            }
                        } for month in range(1, 13)
                    }
                }
        else:
            new_year_data = {
                "month": {
                    str(month): {
                        "[placeholder]": {
                            "monthly_hours": {
                                "entry_data": []
                            }
                        }
                    } for month in range(1, 13)
                }
            }

        with open(json_filepath, 'w') as file:
            json.dump(new_year_data, file, indent=4)

    return json_filepath

def save_new_crew_member(crew_member_name, crew, month, year, schedule_type):
    #def load_and_save_data():
    if schedule_type == "Overtime":
        schedule_prefix = "OT"
    else:
        schedule_prefix = "WS"

    shared_path = get_shared_path() or os.getcwd()
    json_filepath = os.path.join(shared_path, "SaveFiles", f"{schedule_prefix}_{crew}_{year}.json")
   
    # Load the entire JSON data from the file
    with open(json_filepath, 'r') as file:
        data = json.load(file)

    # Get the specific month data from the loaded JSON data
    month_data = data["month"].get(str(month), {})

    # Replace the placeholder entry if it exists
    if "[placeholder]" in month_data:
        month_data[crew_member_name] = month_data["[placeholder]"]
        del month_data["[placeholder]"]

    # Create a new entry for the crew member in the month data
    if schedule_prefix == "OT":
        month_data[crew_member_name] = {
            "monthly_hours": {
                "starting_asking_hours": 0,
                "starting_working_hours": 0,
                "total_asking_hours": 0,
                "total_working_hours": 0,
                "asking_hours_data": [],
                "working_hours_data": []
            }
        }
    elif schedule_prefix == "WS":
        month_data[crew_member_name] = {
            "monthly_hours": {
                "entry_data": []
            }
        }

    # Update the month data in the loaded JSON data
    data["month"][str(month)] = month_data

    # Save the updated JSON data back to the file
    with open(json_filepath, 'w') as file:
        json.dump(data, file, indent=4)
        
    load_hours_data_from_json(crew, month, year, schedule_type)
        
def remove_crew_member(crew_member_name, crew, month, year, schedule_type):
    if schedule_type == "Overtime":
        schedule_prefix = "OT"
    else:
        schedule_prefix = "WS"

    shared_path = get_shared_path() or os.getcwd()
    json_filepath = os.path.join(shared_path, "SaveFiles", f"{schedule_prefix}_{crew}_{year}.json")
   
    # Load the entire JSON data from the file
    with open(json_filepath, 'r') as file:
        data = json.load(file)

    # Get the specific month data from the loaded JSON data
    month_data = data["month"].get(str(month), {})

    # Remove the crew member from the month data
    if crew_member_name in month_data:
        del month_data[crew_member_name]

    # Update the month data in the loaded JSON data
    data["month"][str(month)] = month_data

    # Save the updated JSON data back to the file
    with open(json_filepath, 'w') as file:
        json.dump(data, file, indent=4)
        
    load_hours_data_from_json(crew, month, year, schedule_type)

def adjust_crew_member_starting_hours(crew_member_name, crew, year, new_starting_working_hours, new_starting_asking_hours):
    schedule_prefix = "OT"
    shared_path = get_shared_path() or os.getcwd()
    json_filepath = os.path.join(shared_path, "SaveFiles", f"{schedule_prefix}_{crew}_{year}.json")
   
    # Load the entire JSON data from the file
    with open(json_filepath, 'r') as file:
        data = json.load(file)

    # Get the crew member's data for January
    january_data = data["month"]["1"].get(crew_member_name)
    if january_data:
        # Calculate the adjustment in starting hours
        working_hours_adjustment = new_starting_working_hours - january_data["monthly_hours"]["starting_working_hours"]
        asking_hours_adjustment = new_starting_asking_hours - january_data["monthly_hours"]["starting_asking_hours"]

        # Update the starting hours for January
        january_data["monthly_hours"]["starting_working_hours"] = new_starting_working_hours
        january_data["monthly_hours"]["starting_asking_hours"] = new_starting_asking_hours

        # Update the total hours for January
        january_data["monthly_hours"]["total_working_hours"] = january_data["monthly_hours"]["total_working_hours"] + working_hours_adjustment
        january_data["monthly_hours"]["total_asking_hours"] = january_data["monthly_hours"]["total_asking_hours"] + working_hours_adjustment + asking_hours_adjustment

        # Update the starting hours and total hours for subsequent months
        for month in range(2, 13):
            month_str = str(month)
            month_data = data["month"][month_str].get(crew_member_name)
            if month_data:
                month_data["monthly_hours"]["starting_working_hours"] = month_data["monthly_hours"]["starting_working_hours"] + working_hours_adjustment
                month_data["monthly_hours"]["starting_asking_hours"] = month_data["monthly_hours"]["starting_asking_hours"] + asking_hours_adjustment
                month_data["monthly_hours"]["total_working_hours"] = month_data["monthly_hours"]["total_working_hours"] + working_hours_adjustment
                month_data["monthly_hours"]["total_asking_hours"] = month_data["monthly_hours"]["total_asking_hours"] + asking_hours_adjustment

    # Save the updated JSON data back to the file
    with open(json_filepath, 'w') as file:
        json.dump(data, file, indent=4)

def load_hours_data_from_json(crew, month, year, schedule_type):
    month_data = data_cache.get_data(crew, month, year, schedule_type)
    if not month_data:
        logging.error(f"No data found for month {month}")
        return {}

    crew_member_hours = {}
    for name, member_data in month_data.items():
        if name != "[placeholder]":
            crew_member_hours[name] = CrewMemberHours.from_dict({name: member_data})

    return crew_member_hours

def change_crew_member_name(old_name, new_name, crew, month, year, schedule_type):
    if schedule_type == "Overtime":
        schedule_prefix = "OT"
    else:
        schedule_prefix = "WS"

    shared_path = get_shared_path() or os.getcwd()
    json_filepath = os.path.join(shared_path, "SaveFiles", f"{schedule_prefix}_{crew}_{year}.json")
   
    # Load the entire JSON data from the file
    with open(json_filepath, 'r') as file:
        data = json.load(file)

    # Get the specific month data from the loaded JSON data
    month_data = data["month"].get(str(month), {})

    # Update the crew member name in the month data
    if old_name in month_data:
        month_data[new_name] = month_data.pop(old_name)

    # Update the month data in the loaded JSON data
    data["month"][str(month)] = month_data

    # Save the updated JSON data back to the file
    with open(json_filepath, 'w') as file:
        json.dump(data, file, indent=4)
        
    load_hours_data_from_json(crew, month, year, schedule_type)

def save_hours_data_to_json(crew_member_hours, crew, year, schedule_type, month):
    if schedule_type == "Overtime":
        schedule_prefix = "OT"
    else:
        schedule_prefix = "WS"

    shared_path = get_shared_path() or os.getcwd()
    json_filepath = os.path.join(shared_path, "SaveFiles", f"{schedule_prefix}_{crew}_{year}.json")
   
    # Load existing data from the JSON file
    with open(json_filepath, 'r') as file:
        existing_data = json.load(file)

    # Create the month entry in the existing data if it doesn't exist
    if str(month) not in existing_data['month']:
        existing_data['month'][str(month)] = {}

    # Remove the placeholder entry if it exists
    if "[placeholder]" in existing_data['month'][str(month)]:
        del existing_data['month'][str(month)]["[placeholder]"]

    # Update the crew member data for the specific month
    for name, crew_member in crew_member_hours.items():
        if schedule_type == "Overtime":
            existing_data['month'][str(month)][name] = {
                "monthly_hours": {
                    "starting_asking_hours": crew_member.monthly_hours['starting_asking_hours'],
                    "starting_working_hours": crew_member.monthly_hours['starting_working_hours'],
                    "total_asking_hours": crew_member.monthly_hours['total_asking_hours'],
                    "total_working_hours": crew_member.monthly_hours['total_working_hours'],
                    "asking_hours_data": crew_member.monthly_hours['asking_hours_data'],
                    "working_hours_data": crew_member.monthly_hours['working_hours_data']
                }
            }
        else:
            existing_data['month'][str(month)][name] = {
                "monthly_hours": {
                    "entry_data": crew_member.monthly_hours[str(month)]['entry_data']
                }
            }

    # Update subsequent months' starting hours and total hours
    update_subsequent_months(existing_data, crew, year, schedule_type, month)
    
    # Save the updated data back to the JSON file
    with open(json_filepath, 'w') as file:
        json.dump(existing_data, file, indent=4)

def update_subsequent_months(existing_data, crew, year, schedule_type, month):
    if schedule_type == "Overtime":
        for subsequent_month in range(month + 1, 13):
            subsequent_month_str = str(subsequent_month)
            if subsequent_month_str in existing_data['month']:
                for name, crew_member_data in existing_data['month'][subsequent_month_str].items():
                    if name != "[placeholder]":
                        previous_month_str = str(subsequent_month - 1)
                        previous_month_data = existing_data['month'][previous_month_str][name]['monthly_hours']
                        crew_member_data['monthly_hours']['starting_asking_hours'] = previous_month_data['total_asking_hours']
                        crew_member_data['monthly_hours']['starting_working_hours'] = previous_month_data['total_working_hours']
                        crew_member_data['monthly_hours']['total_asking_hours'] = previous_month_data['total_asking_hours'] + sum(
                            int(hours) for hours in crew_member_data['monthly_hours']['asking_hours_data'] if hours.isdigit()
                        )
                        crew_member_data['monthly_hours']['total_working_hours'] = previous_month_data['total_working_hours'] + sum(int(hours) for hours in crew_member_data['monthly_hours']['working_hours_data'] if hours.isdigit())
      
def move_person_data(user_selections, moved_personnel, schedule_type):
    if schedule_type == "Overtime":
        schedule_prefix = "OT"
    else:
        schedule_prefix = "WS"

    shared_path = get_shared_path() or os.getcwd()
    json_filepath = os.path.join(shared_path, "SaveFiles", f"{schedule_prefix}_{user_selections['selected_crew']}_{user_selections['selected_year'].year}.json")

    # Load the entire JSON data from the file
    with open(json_filepath, 'r') as file:
        data = json.load(file)

    # Iterate over all the months in the JSON data
    for month in data["month"]:
        # Get the specific month data from the loaded JSON data
        month_data = data["month"][month]

        # Create a list of crew member names and their data
        crew_member_list = [(name, month_data[name]) for name in month_data]

        # Adjust the order of personnel based on the moved personnel list
        for moved_name, new_position in moved_personnel:
            # Find the current position of the moved personnel
            current_position = next((i for i, (name, _) in enumerate(crew_member_list) if name == moved_name), None)

            # Move the personnel to the new position if found
            if current_position is not None:
                crew_member_list.insert(new_position, crew_member_list.pop(current_position))

        # Update the month data with the reordered personnel
        month_data = {name: data for name, data in crew_member_list}

        # Update the month data in the loaded JSON data
        data["month"][month] = month_data

    # Save the updated JSON data back to the file
    with open(json_filepath, 'w') as file:
        json.dump(data, file, indent=4)