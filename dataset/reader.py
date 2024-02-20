

class CTTFileReader:

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {
            'courses': {},
            'rooms': {},
            'curricula': {},
            'unavailability_constraints': {}
        }
        self._parse_file()

    def _parse_file(self):
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
        
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if ':' in line and not line.isupper() and "Name" not in line:
                self._parse_count_line(line)
            elif line.isupper() and ':' in line:
                current_section = line[:-1].lower()
            else:
                self._parse_section_data(current_section, line)


    def _parse_count_line(self, line):
        key, value = line.split(':', 1)
        key = key.strip().lower().replace(' ', '_') + '_count'
        self.data[key] = int(value)


    def _parse_section_data(self, current_section, line):
        if current_section == 'courses':
            self._parse_course_line(line)
        elif current_section == 'rooms':
            self._parse_room_line(line)
        elif current_section == 'curricula':
            self._parse_curriculum_line(line)
        elif current_section == 'unavailability_constraints':
            self._parse_unavailability_line(line)


    def _parse_course_line(self, line):
        course_id, teacher_id, lectures, min_days, students = line.split()
        self.data['courses'][course_id] = {
            'teacher_id': teacher_id,
            'lectures': int(lectures),
            'min_days': int(min_days),
            'students': int(students)
        }


    def _parse_room_line(self, line):
        room_id, capacity = line.split()
        self.data['rooms'][room_id] ={'capacity': int(capacity)}


    def _parse_curriculum_line(self, line):
        curriculum_id, *courses = line.split()
        self.data['curricula'][curriculum_id] = courses


    def _parse_unavailability_line(self, line):
        if 'END.' not in line:
            course_id, day, time_slot = line.split()
            self.data['unavailability_constraints'][course_id] = {'day' : day, 'time_slot' : time_slot}


    def get_data(self):
        return self.data
