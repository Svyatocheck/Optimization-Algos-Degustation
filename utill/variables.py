disruption_scenarios = [
    {
        'type': 'instructor_unavailability',
        'details': {
            'instructor_id': 't001',
            'unavailable_periods': [(2, 3), (3, 4)]
        }
    },
    {
        'type': 'course_period_change',
        'details': {
            'course_id': 'c001',
            'new_periods': [(1, 2), (2, 1)]
        }
    },
    {
        'type': 'student_number_increase',
        'details': {
            'course_id': 'c002',
            'new_student_count': 120
        }
    },
    {
        'type': 'room_unavailability',
        'details': {
            'room_id': 'A',
            'unavailable_periods': [(1, 3), (2, 4)]
        }
    }
]


FILE_PATH = ''
ARCHIEVE_PATH = ''
