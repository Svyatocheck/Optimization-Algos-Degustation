import streamlit as st
import pandas as pd
import json

from dataset.reader import CTTFileReader
from utill.optimization import *
from utill import *
from utill.variables import *

import pandas as pd
import numpy as np

DATASET_FILE_PATH = FILE_PATH
BEST_SOLUTION_PATH = ARCHIEVE_PATH

# Streamlit app setup
st.set_page_config(layout="wide")
st.title("Curriculum Timetables")


def read_dataset():
    file_reader = CTTFileReader(DATASET_FILE_PATH)
    ctt_data = file_reader.get_data()
    return ctt_data


def parse_data():
    with open(BEST_SOLUTION_PATH, 'r') as file:
        data = json.load(file)
    schedule = data["Solution"][0]
    ctt_data = read_dataset()
    curricula = ctt_data['curricula']
    return schedule, curricula


def extract_teacher(courses_id):
    ctt_data = read_dataset()
    courses = ctt_data['courses']
    return courses[courses_id]['teacher_id']


def create_full_timetable(curriculum_courses, num_timeslots, num_days):
    full_timetable = [[[] for _ in range(num_days)]
                      for _ in range(num_timeslots)]

    # Compile schedules for all courses in the curriculum
    for course_id in curriculum_courses:
        if course_id in schedule:
            course_schedule = schedule[course_id]
            if len(course_schedule) == 3 and type(course_schedule[0]) != list:
                full_timetable[course_schedule[1]][course_schedule[0]].append(
                    f"{course_id} - {course_schedule[2]} - {extract_teacher(course_id)}")
            else:
                for day, timeslot, info in course_schedule:
                    full_timetable[timeslot][day].append(
                        f"{course_id} - {info} - {extract_teacher(course_id)}")
    return full_timetable


def check_overlap_and_color(timetable):
    html_table = "<table style='width:100%'>"
    html_table += "<tr><th>Timeslot</th>"
    for day in range(1, len(timetable[0]) + 1):
        html_table += f"<th>Day {day}</th>"
    html_table += "</tr>"

    for timeslot, day_data in enumerate(timetable):
        html_table += "<tr>"
        html_table += f"<td>{timeslot}</td>"
        for day in day_data:
            cell_content = "<br>".join(day)
            cell_color = "red" if len(day) > 1 else ""  # Red if overlapping
            html_table += f"<td style='background-color:{cell_color};'>{cell_content}</td>"
        html_table += "</tr>"

    html_table += "</table>"
    return html_table


def create_timetable(schedule_data, num_timeslots, num_days):
    timetable = [["" for _ in range(num_days)] for _ in range(num_timeslots)]

    # Normalize lectures to tuples
    if isinstance(schedule_data, list) and schedule_data and isinstance(schedule_data[0], (list, tuple)):
        schedule_data = [tuple(lecture) for lecture in schedule_data]
    else:
        schedule_data = [tuple(schedule_data)]
    
    for entry in schedule_data:
        if len(entry) == 3:
            day, timeslot, info = entry
            if 0 <= timeslot < num_timeslots and 0 <= day < num_days:
                timetable[timeslot][day] = info
            else:
                st.error(f"Invalid timeslot/day in entry: {entry}")
        else:
            st.error(f"Invalid entry format: {entry}")

    return timetable


# Get timetable data
schedule, curricula = parse_data()

# Define the range of timeslots and days
num_timeslots = 6
num_days = 5

# Dynamically create tabs
tabs = st.tabs(
    [f"Curriculum {curriculum_id}" for curriculum_id in curricula.keys()])

for tab, (curriculum_id, courses) in zip(tabs, curricula.items()):
    with tab:
        st.header(f"Curriculum: {curriculum_id}")
        courses = courses[1:]

        full_timetable_data = create_full_timetable(courses, num_timeslots, num_days)
        color_coded_html = check_overlap_and_color(full_timetable_data)
        st.markdown(color_coded_html, unsafe_allow_html=True)

        for course_id in courses:
            if course_id in schedule:
                course_schedule = schedule[course_id]
                timetable_data = create_timetable(
                    course_schedule, num_timeslots, num_days)
                df = pd.DataFrame(timetable_data, columns=[f"Day {i+1}" for i in range(num_days)])
                df.index.name = "Timeslot"
                st.subheader(f"Course: {course_id}")
                st.table(df)
            else:
                st.write(f"No schedule data available for {course_id}")
