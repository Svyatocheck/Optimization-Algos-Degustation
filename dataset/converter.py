

class CTTFileConverter:

    def __init__(self, ctt_data) -> None:
        self.set_of_solutions = {}

        # Read available data
        self.population = {'Courses': [course_name for course_name in ctt_data['courses'].keys()]}
        self.ctt_data = ctt_data
        
        # Generate/Make data
        self.days = [i for i in range(ctt_data["days_count"])]
        self.timeslots = [i for i in range(ctt_data["periods_per_day_count"])]
        self.rooms = [room for room in self.ctt_data['rooms'].keys()]
        self._convert_data()


    def _convert_data_curricula(self):
        for curricula_id, composition in self.ctt_data['curricula'].items():
            possible_schedules = [
                (day, timeslot, room)
                for index, course_id in enumerate(composition)
                for day in self.days
                for timeslot in self.timeslots
                for room in self.rooms
                if index != 0 and self.ctt_data['courses'][course_id]['students'] <= next(
                    r['capacity'] for r in self.ctt_data['rooms'] if r['room_id'] == room
                )
                and (day, timeslot) not in self.ctt_data['unavailability_constraints'].get(course_id, [])
            ]
            self.set_of_solutions[curricula_id] = possible_schedules


    def _convert_data(self):
        for course_id, course_info in self.ctt_data['courses'].items():
            possible_schedules = []
            for day in self.days:
                for timeslot in self.timeslots:
                    for room in self.rooms:
                        # Check if the room is big enough
                        if course_info['students'] <= next((value['capacity'] for key, value in self.ctt_data['rooms'].items() if key == room), 0):
                            
                            # Check for teacher availability
                            if (day, timeslot) not in self.ctt_data['unavailability_constraints'].get(course_id, []):
                                possible_schedules.append(
                                    (day, timeslot, room))
            self.set_of_solutions[course_id] = possible_schedules

    
    def generate_timeslots(self):
        possible_schedules = []
        for day in self.days:
            for timeslot in self.timeslots:
                for room in self.rooms:
                    possible_schedules.append((day, timeslot, room))
        return possible_schedules
    

    def get_population_data(self):
        self.population['Timeslots'] = self.generate_timeslots()
        return self.population


    def get_set_of_solutions(self):
        return self.set_of_solutions
    
        
