# PEP8 Compliant Guidance
# Standard Library Imports

# Third-Party Library Imports

# Local Application/Library Specific Imports


class CrewMemberHours:
    """
    the CrewMemberHours class is designed to encapsulate and manage the monthly hours 
    data for a single crew member. It provides methods to update, retrieve, and convert 
    the hours data to and from dictionaries. 
    
    This class is used in conjunction with other parts of the application to handle and 
    process crew member hours data.
    """
    def __init__(self, name=''):
        """
        The constructor method initializes a new instance of the CrewMemberHours class.

        Args:
            name (str, optional): name of the crew member. Defaults to ''.
        """
        self.name = name
        self.monthly_hours = {}

    def update_hours(self, starting_asking_hours, starting_working_hours, total_asking_hours, total_working_hours, asking_hours_data, working_hours_data):
        """
        This method is used to update or initialize the monthly hours data for a specific month.

        Args:
            month (int): schedule month for which to update the hours data.
            starting_asking_hours (int): starting asking hours for the month.
            starting_working_hours (int): starting working hours for the month.
            total_asking_hours (int): total asking hours for the month.
            total_working_hours (int): total working hours for the month.
            asking_hours_data (list): asking hour entry data for the month.
            working_hours_data (list): working hour entry data for the month.
        """
        self.monthly_hours = {
            'starting_asking_hours': starting_asking_hours,
            'starting_working_hours': starting_working_hours,
            'total_asking_hours': total_asking_hours,
            'total_working_hours': total_working_hours,
            'asking_hours_data': asking_hours_data,
            'working_hours_data': working_hours_data
        }

    def get_hours(self):
        """
        Retrieves the monthly hours data for a specific month.

        Args:
            month (int): month for which to retrieve the hours data.
            
        Returns:
            dict: returns the dictionary associated with self.monthly_hours[str(month)] 
            if it exists, or a default dictionary with initial values if the key doesn't exist.
        """
        return self.monthly_hours

    def to_dict(self):
        """
        Counterpart to the from_dict class method, this instance method is used to convert
        the CrewMemberHours instance to a dictionary representation. This is useful for
        serialization and storing data in a format that can be easily converted back to
        CrewMemberHours instances.

        Serializes the data.

        Returns:
            dict: a dictionary with the following structure:
            {
                "crew_member_name": {
                    "monthly_hours": {
                        "starting_asking_hours": 0,
                        "starting_working_hours": 0,
                        "total_asking_hours": 0,
                        "total_working_hours": 0,
                        "asking_hours_data": [],
                        "working_hours_data": []
                    }
                }
            }
        """
        return {
            self.name: {
                "monthly_hours": self.get_hours()
            }
        }

    @classmethod
    def from_dict(cls, data):
        """
        Counterpart to the to_dict method, this class method creates a new instance of the
        CrewMemberHours class from a dictionary data allowing for easy conversion from json 
        data to CrewMemberHours instances. 
        
        Deserializes the data.

        Args:
            data (dict): keys are expected to be crew member names, and the values are 
            dictionaries containing the monthly hours data.

        Returns:
            CrewMemberHours: An instance of CrewMemberHours class populated with the data.
        """
        name = list(data.keys())[0]
        crew_member = cls(name)
        
        if "monthly_hours" in data[name]:
            crew_member.monthly_hours = data[name]["monthly_hours"]
        else:
            crew_member.monthly_hours = {}
        
        return crew_member
    

    def __repr__(self):
        """
        A special method that provides a string representation of the CrewMemberHours instance
        for debugging purposes

        Returns:
            str: returns a string in the format.. 
            "CrewMemberHours(name={self.name}, monthly_hours={self.monthly_hours})"
            ..which can be useful for debugging and logging purposes.
        """
        return f"CrewMemberHours(name={self.name}, monthly_hours={self.monthly_hours})"

