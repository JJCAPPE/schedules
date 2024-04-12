import pandas as pd
import streamlit as st

# Inputs

subjects_students = 'Students Subjects.xlsx'

timetable_xlsx = 'Managebac Timetables.xlsx'

rooms_excel = 'Student Schedule Finder Rooms.xlsx'

data = pd.read_excel(subjects_students)

timetable = pd.read_excel(timetable_xlsx)

rooms_df = pd.read_excel(rooms_excel)


def eval_without_ollama(code):
    instruction = f"data.loc[data['Code'] == '{code}', 'Subject'].tolist()"
    exec_result = eval(instruction)
    return exec_result


def evaluate(instructions):
    try:
        instructions = instructions.replace("`", "").replace("´", "")
        data_index = instructions.find('data')
        if data_index != -1:
            cleaned_1 = instructions[data_index:]
        else:
            print(f"Instruction: {instructions}")
            raise ValueError("'data' not found in instructions")
        print(cleaned_1)
        exec_result = eval(cleaned_1)
        return exec_result
    except Exception as e:
        return f"Error: {str(e)}"


def find_times(subjects, day):
    periods = []

    for i in range(len(subjects)):
        period = find_class_schedule(subjects[i], day)
        if period != 0:
            periods.append(period)

    periods_separate = []

    for item in periods:
        if isinstance(item, str) and '&' in item:
            numbers = [int(num.strip()) for num in item.split('&')]
            periods_separate.extend(numbers)
        elif isinstance(item, int):
            periods_separate.append(item)

    all_numbers = list(range(1, 10))

    missing_numbers = [num for num in all_numbers if num not in periods_separate]

    return missing_numbers

def find_schedule(subjects, daynumber, rooms_df, day):
    periods = []
    room = []
    found_rooms = []

    for i in range(len(subjects)):
        period = find_class_schedule(subjects[i], day)
        if period != 0:
            periods.append(period)
            room.append(subjects[i])

    updated_periods = []
    updated_room = []

    for idx, item in enumerate(periods):
        if isinstance(item, str) and '&' in item:
            numbers = [int(num.strip()) for num in item.split('&')]
            updated_periods.extend(numbers)
            updated_room.extend([room[idx]] * len(numbers))  # Repeat the room name for each split period
        elif isinstance(item, int):
            updated_periods.append(item)
            updated_room.append(room[idx])

    # Match each period with its corresponding room for the given day
    for period_num in updated_periods:
        day_schedule = rooms_df[rooms_df['Day Number'] == daynumber]
        matching_room = day_schedule[day_schedule['Period Number'] == period_num]['Location'].values
        if len(matching_room) > 0:
            found_rooms.append(matching_room[0])
        else:
            found_rooms.append('No given room')

    return updated_periods, updated_room, found_rooms


def find_code_by_surname(data_frame, surname):
    data_frame['Surname'] = data_frame['Surname'].str.lower()

    # Search for the provided surname
    filtered_data = data_frame.loc[data_frame['Surname'] == surname.lower(), 'Code'].drop_duplicates()

    # Check if any rows are found
    if not filtered_data.empty:
        return filtered_data.tolist()
    else:
        return None

def convert_day_to_number(day_name):
    
    day_name = day_name.lower()

    day_mapping = {
        'monday': 1,
        'tuesday': 2,
        'wednesday': 3,
        'thursday': 4,
        'friday': 5,
    }

    return day_mapping.get(day_name)

def find_code_by_name_and_surname(data_frame, name, surname):
    # Convert name and surname to lowercase for case-insensitive matching
    name = name.lower()
    surname = surname.lower()

    # Search for the provided name and surname combination
    filtered_data = data_frame.loc[
        (data_frame['Name'].str.lower() == name) & (data_frame['Surname'].str.lower() == surname), 'Code']

    # Check if any rows are found
    if not filtered_data.empty:
        return filtered_data.iloc[0]  # Assuming there's only one unique code for the combination
    else:
        return None


def find_email_by_code(data_frame, code):
    # Search for the provided code
    filtered_data = data_frame.loc[data_frame['Code'] == code, 'Email']

    # Check if any rows are found
    if not filtered_data.empty:
        return filtered_data.iloc[0]
    else:
        return None


def find_name_by_code(data_frame, code):
    data_frame['Surname'] = data_frame['Surname'].str.lower()

    # Search for the provided surname
    filtered_data = data_frame.loc[data_frame['Code'] == code, 'Name']

    # Check if any rows are found
    if not filtered_data.empty:
        return filtered_data.iloc[0]
    else:
        return None


def convert_to_times(numbers):
    time_table = {
        1: '08:50 to 9:35', 2: '09:35 to 10:20', 3: '10:20 to 11:05',
        4: '11:20 to 12:05', 5: '12:05 to 12.50', 6: '12:50 to 13:35',
        7: '14:15 to 14:55', 8: '14:55 to 15:35', 9: '15:35 to 16:15'
    }
    times = [time_table[num] for num in numbers]
    return times


def find_class_schedule(class_name, day):
    # Filter DataFrame based on class name
    class_schedule_df = timetable[timetable['Class Name'] == class_name]

    # Retrieve periods for the specified day
    periods = class_schedule_df[day].values[0]

    # Check if periods are not NaN (i.e., class is taught on the specified day)
    if pd.notnull(periods):
        return periods
    else:
        return 0


def prepare(day, surname):
    name = ""

    student_code = find_code_by_surname(data, surname)

    if len(student_code) == 0:
        return "", "No student found with the provided surname."
    elif len(student_code) == 1:
        student_code = student_code[0]
        name = find_name_by_code(data, student_code)
    else:
        names_to_try = []
        for i in range(len(student_code)):
            name_temp = find_name_by_code(data, student_code[i])
            names_to_try.append(name_temp)
        selected_student_name = st.selectbox("Select a student:", names_to_try)
        if selected_student_name:
            student_code = find_code_by_name_and_surname(data, selected_student_name, surname)
            name = selected_student_name

    subjects = eval_without_ollama(student_code)

    periods = find_times(subjects, day)

    times = convert_to_times(periods)

    email = find_email_by_code(data, student_code)

    daynumber = convert_day_to_number(day)

    updated_periods, updated_room, found_rooms = find_schedule(subjects, daynumber, rooms_df, day)

    return name, student_code, times, email, updated_periods, updated_room, found_rooms


def main():
    st.title("Student Schedule Finder")
    day = st.selectbox("Select a day of the week:", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    surname = st.text_input("Enter student's surname:")
    name = ""
    times = []
    email = ""
    updated_periods = []
    updated_room = []
    found_rooms = []

    if surname:

        name, student_code, times, email, updated_periods, updated_room, found_rooms = prepare(day, surname)

        periods_busy = convert_to_times(updated_periods)

    if st.button("Find"):
        if not times:
            return "", "No avaiable times"
        else:
            st.markdown(f"### Student's Name: **{name} {surname}**")
            st.markdown(f"### Student's Email: **{email}**")
            st.metric(value=f"{day}", delta=f"{len(times)} Free Periods")
            st.write(f"Available {day} Times:")
            time_df = pd.DataFrame({
                'Time Slot': times
            })
            st.dataframe(time_df)
            st.write("Schedule:")
            schedule_df = pd.DataFrame({
                'Period': updated_periods,
                'Time': periods_busy,
                'Subject': updated_room,
                'Room': found_rooms
            })
            st.dataframe(schedule_df)


if __name__ == '__main__':
    main()
    