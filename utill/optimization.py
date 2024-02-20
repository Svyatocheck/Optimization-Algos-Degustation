from copy import deepcopy
from collections import defaultdict


def get_lectures_count(ctt_data):
    courses_dict = ctt_data['courses']
    lectures_count = {}
    for course_id, course_info in courses_dict.items():
        lectures_count[course_id] = course_info['lectures']
    return lectures_count


def set_maximum_solution_elements(ctt_data):
    lectures_count = get_lectures_count(ctt_data)
    maximum_number_of_solution_elements = {}
    for course_id, num_lectures in lectures_count.items():
        maximum_number_of_solution_elements[course_id] = num_lectures if num_lectures > 1 else 2
    return maximum_number_of_solution_elements


def get_lectures_count(ctt_data):
    courses_dict = ctt_data['courses']
    lectures_count = {}
    for course_id, course_info in courses_dict.items():
        lectures_count[course_id] = course_info['lectures']
    return lectures_count


def find_shared_courses(curricula):
    # Find courses that are present in multiple curricula
    shared_courses = {}
    for curriculum_id, courses in curricula.items():
        for course in courses:
            if course in shared_courses:
                shared_courses[course].add(curriculum_id)
            else:
                shared_courses[course] = {curriculum_id}

    # Filter out courses that are not shared across curricula
    return {course: curricula_ids for course, curricula_ids in shared_courses.items() if len(curricula_ids) > 1}


def check_shared_courses_schedule(solution, shared_courses):
    # Track the timeslot for each shared course
    course_timeslots = {}

    for curriculum_id, courses_schedule in solution.items():
        for course_id, timeslots in courses_schedule:
            if course_id in shared_courses:
                if course_id not in course_timeslots:
                    course_timeslots[course_id] = set(timeslots)
                else:
                    if set(timeslots) != course_timeslots[course_id]:
                        return False  # Inconsistent scheduling for shared course

    return True  # All shared courses are consistently scheduled


def calculate_hard_constraints_penalty(timetable, data):
    HIGH_PENALTY = 500
    MIN_WORKING_DAYS_PENALTY = 5
    ROOM_STABILITY_PENALTY = 1

    penalty = 0
    teacher_schedules = {}
    curriculum_lectures = {curriculum: [] for curriculum in data['curricula']}  # Initialize as lists

    # Aggregate all lectures for each curriculum
    for course, lectures in timetable.items():
        for curriculum, courses in data['curricula'].items():
            if course in courses:
                if isinstance(lectures, list) and lectures and isinstance(lectures[0], (list, tuple)):
                    lectures = [tuple(lecture) for lecture in lectures]
                else:
                    lectures = [tuple(lectures)]
                curriculum_lectures[curriculum].extend(lectures)
                
    # Check for overlaps within each curriculum
    for curriculum, lectures in curriculum_lectures.items():
        if isinstance(lectures, list) and lectures and isinstance(lectures[0], (list, tuple)):
            lectures = [tuple(lecture) for lecture in lectures]
        else:
            lectures = [tuple(lectures)]
        # Check each lecture against all others in the curriculum
        for i in range(len(lectures)):
            for j in range(i + 1, len(lectures)):
                if lectures[i][0] == lectures[j][0] and lectures[i][1] == lectures[j][1]:  # Same day and timeslot
                    print(f"Overlap detected in {curriculum} between lectures {lectures[i]} and {lectures[j]}")
                    penalty += HIGH_PENALTY

    # No Teacher Clashes
    for course, lectures in timetable.items():
        teacher_id = data['courses'][course]['teacher_id']
        if isinstance(lectures, list) and lectures and isinstance(lectures[0], (list, tuple)):
            lectures = [tuple(lecture) for lecture in lectures]
        else:
            lectures = [tuple(lectures)]
        
        for day, timeslot, _ in lectures:
            if teacher_id not in teacher_schedules:
                teacher_schedules[teacher_id] = set()
            if (day, timeslot) in teacher_schedules[teacher_id]:
                penalty += HIGH_PENALTY
            teacher_schedules[teacher_id].add((day, timeslot))

    for course, lectures in timetable.items():
        course_data = data['courses'][course]
        if isinstance(lectures, list) and lectures and isinstance(lectures[0], (list, tuple)):
            lectures = [tuple(lecture) for lecture in lectures]
        else:
            lectures = [tuple(lectures)]
        
        # Minimum Working Days Constraint
        unique_days = len(set(day for day, _, _ in lectures))
        if unique_days < data['days_count']:
            penalty += MIN_WORKING_DAYS_PENALTY * (data['days_count'] - unique_days)

        # Room Stability Constraint
        used_rooms = set(room_id for _, _, room_id in lectures)
        if len(used_rooms) > 1:
            penalty += ROOM_STABILITY_PENALTY * (len(used_rooms) - 1)

    penalty += calculate_class_neighbors_penalty(timetable, data)
    return penalty


def calculate_class_neighbors_penalty(timetable, data):
    penalty = 0
    GAP_PENALTY = 10  # Define a penalty value for each gap

    for course, lectures in timetable.items():
        if isinstance(lectures, list) and lectures and isinstance(lectures[0], (list, tuple)):
            lectures = [tuple(lecture) for lecture in lectures]
        else:
            lectures = [tuple(lectures)]
        
        # Filter out non-tuple elements
        lectures = [l for l in lectures if isinstance(l, tuple) and len(l) >= 2]

        # Sort lectures by day and timeslot for sequential analysis
        sorted_lectures = sorted(lectures, key=lambda x: (x[0], x[1]))  # x[0] is day, x[1] is timeslot

        for i in range(len(sorted_lectures) - 1):
            current_day, current_timeslot = sorted_lectures[i][0], sorted_lectures[i][1]
            next_day, next_timeslot = sorted_lectures[i + 1][0], sorted_lectures[i + 1][1]
            # Check for gaps on the same day
            if current_day == next_day and next_timeslot - current_timeslot > 1:
                penalty += GAP_PENALTY  # Add penalty for each gap

    return penalty



# def apply_disruption(solution, disruption, data):
#     # Assuming disruption is a dictionary with keys like 'type', 'teacher_id', or 'room_id'
#     disrupted_solution = dict(solution)
#     if disruption['type'] == 'instructor_unavailability':
#         # Identify all timeslots with the unavailable teacher and remove or reschedule them
#         unavailable_teacher = disruption['details']['instructor_id']
#         for course_id, timeslots in disrupted_solution.items():
#             if data['courses'][course_id]['teacher_id'] == unavailable_teacher:
#                 # Remove or reschedule timeslots
#                 disrupted_solution[course_id] = [
#                     ts for ts in timeslots if ts[2] != unavailable_teacher]
#     return disrupted_solution


# def calculate_robustness(solution, data, disruptions):
#     original_penalty = calculate_penalty_P(solution, data)
#     robustness_score = 0

#     for disruption in disruptions:
#         # Apply the disruption to the solution
#         disrupted_solution = apply_disruption(solution, disruption, data)

#         # Calculate the penalty for the disrupted solution
#         disrupted_penalty = calculate_penalty_P(disrupted_solution, data)

#         # Measure the impact of the disruption
#         impact = disrupted_penalty - original_penalty
#         robustness_score += impact

#     return robustness_score
