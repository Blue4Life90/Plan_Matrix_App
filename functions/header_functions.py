# PEP8 Compliant Guidance
# Standard Library Imports
import os
import logging
import calendar
import datetime as dt
from datetime import datetime, timedelta

# Third-Party Library Imports

# Local Application/Library Specific Imports
from constants import log_file

# Logging Format
logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file, 
                    filemode='a')

def get_crew_shifts(crew, date_value):
    """
    Retrieve the crew shifts for the selected crew and date from the DATELOOP_FILEPATH file.

    Args:
        Crew (str): The selected crew.
        date_value (dt.datetime): The selected date.

    Returns:
        list[str]: A list of crew shift values for the selected crew and date.
    """
    try:
        # Define the base start date for the known pattern
        base_date = datetime.strptime('6/22/2023', '%m/%d/%Y')

        # Define the pattern cycle length (28 days)
        cycle_length = 28

        # Define the shifts pattern
        shifts_pattern = {
            'A': ['D'] * 7 + [''] * 7 + ['N'] * 7 + [''] * 7,
            'B': ['N'] * 7 + [''] * 7 + ['D'] * 7 + [''] * 7,
            'C': [''] * 7 + ['N'] * 7 + [''] * 7 + ['D'] * 7,
            'D': [''] * 7 + ['D'] * 7 + [''] * 7 + ['N'] * 7
        }

        def get_crew_shifts(date_str):
            target_date = datetime.strptime(date_str, '%m/%d/%Y')
            delta_days = (target_date - base_date).days
            cycle_day = delta_days % cycle_length

            return {
                'A': shifts_pattern['A'][cycle_day],
                'B': shifts_pattern['B'][cycle_day],
                'C': shifts_pattern['C'][cycle_day],
                'D': shifts_pattern['D'][cycle_day]
            }

        def generate_monthly_shifts(selected_crew, year, month):
            num_days = calendar.monthrange(year, month)[1]
            start_date = datetime(year, month, 1)
            
            monthly_shifts = {
                'A': [],
                'B': [],
                'C': [],
                'D': []
            }

            for day in range(num_days):
                date_str = (start_date + timedelta(days=day)).strftime('%m/%d/%Y')
                shifts = get_crew_shifts(date_str)
                
                for crew in monthly_shifts:
                    monthly_shifts[crew].append(shifts[crew])
            
            crew_shift_list = monthly_shifts[selected_crew]
            
            return crew_shift_list
        
        year = date_value.year
        month = date_value.month
        
        shift_entry_list = generate_monthly_shifts(crew, year, month)
    
    except Exception as e:
        logging.error(f"An error occurred while retrieving crew shifts: {str(e)}")
        return []
    
    return shift_entry_list

def get_selected_values(crew, month, year):
    """
    Store the selected crew, month, and year as a dictionary.

    Args:
        crew (str): The selected crew.
        month (int): The selected month.
        year (int): The selected year.

    Returns:
        dict[str, str | int]: A dictionary containing the selected values.
    """
    values = {
        "selected_crew": crew,
        "selected_month": month,
        "selected_year": year
    }
    return values

def get_user_id():
    """
    Retrieve the user ID of the current user.

    Returns:
        str: The user ID, or "Unknown User" if an error occurred.
    """
    try:
        user_id = os.getlogin()
        return "test_user1" # user_id
    except Exception as e:
        logging.error(f"Failed to retrieve user ID: {str(e)}")
        return "Unknown User"

def crews_list():
    """
    Get a list of available crews.

    Returns:
        list[str]: A list of crew names.
    """
    crews = ["A", "B", "C", "D"]
    return crews

def months_list():
    """
    Get a list of available months.

    Returns:
        list[str]: A list of month names.
    """
    months = []
    for month in range(1, 13):
        months.append(calendar.month_name[month])
    return months

def years_list():
    """
    Get a list of available years.

    Returns:
        list[int]: A list of years ranging from 30 years ago to 30 years in the future.
    """
    current_year = dt.datetime.now().year
    years = []
    
    # generates a list of years from 100 years ago to 100 years in the future
    for year in range(current_year - 30, current_year + 31):
        years.append(year)
    return years

def get_weekday(month, year):
    """
    Get the starting weekday of the given month and year.

    Args:
        month (int): The month.
        year (int): The year.

    Returns:
        int: The starting weekday of the month (1-7, where 1 is Monday and 7 is Sunday).
    """
    # Assign the date to a variable
    Sel_month = dt.date(year, month, 1)
    
    # Get and store the starting weekday of the month as an integer
    starting_weekday = Sel_month.weekday()
    
    # return the starting weekday as an integer + 1 for accuracy
    return starting_weekday + 1

def month_range(month, year):
    """
    Get the number of calendar days in the given month and year.

    Args:
        month (int): The month.
        year (int): The year.

    Returns:
        int: The number of days in the month.
    """
    # Get the number of days in the month (accounts for leap years)
    num_days = calendar.monthrange(year, month)[1]
    return num_days