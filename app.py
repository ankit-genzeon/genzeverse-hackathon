import sqlite3
import datefinder
from getpass import getpass
from werkzeug.security import check_password_hash
import streamlit as st
import joblib
from datetime import datetime, timedelta
import pandas as pd


# Load the model from the file
pipeline = joblib.load('intent_recognition_model.pkl')

conn = sqlite3.connect('timesheets.db')
c = conn.cursor()

def login(employee_id, password):
    c.execute(
        f"SELECT password_hash FROM employees WHERE employee_id = '{employee_id}'")
    result = c.fetchone()

    if result is None:
        return None

    password_hash = result[0]

    if not check_password_hash(password_hash, password):
        return None

    return employee_id


def get_nearest_friday():
    now = datetime.now()
        # weekday() function returns the day of the week as an integer (Monday is 0, Sunday is 6)
        # So, Friday is 4
    days_ahead = 4 - now.weekday()
    if days_ahead < 0: # If it's already past Friday in the current week
        days_ahead += 7
    return now + timedelta(days=days_ahead)

def get_date_from_text(question):
     # If the question contains "this week", return the current date
    if 'this week' in question:
        return datetime.now()
    # If the question contains "last week", return the date one week ago
    elif 'last week' in question:
        return datetime.now() - timedelta(weeks=1)
    else:
        # If the question contains a specific date, return that date
        matches = datefinder.find_dates(question)
        for match in matches:
            return match
    return None

def get_day_from_text(question):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for day in days:
        if day in question.lower():
            return day
    return None

def get_intent(question, model):
    return model.predict([question])[0]

def execute_action(intent, date=None, question=None, employee_id=None, role=None):  # add question as a parameter

    date = get_date_from_text(question)
    day = get_day_from_text(question)

    if date is not None:
        date_str = date.strftime("'%Y-%m-%d'")
    else:
        date_str = None

    if day is not None:
        day_str = f"'{day}'"
    else:
        day_str = None

    if employee_id is not None:
        employee_id = f"'{employee_id}'"

    condition = f"WHERE employee_id = {employee_id}"

    if intent == 'get_past_timesheet':
        c.execute(
             f"SELECT * FROM timesheets {condition} AND week_ending < {date_str}")
        rows = c.fetchall()

        if len(rows) == 0:
            return []
        else:
            return rows  
        


#--------------------------------------------------------------------------------------------------------------------------------------------------------

    # elif intent == 'submit_timesheet':
    #     # Assuming 8 hours for each weekday
    #     c.execute(f"INSERT INTO timesheets (employee_id, week_ending, monday_hours, tuesday_hours, wednesday_hours, thursday_hours, friday_hours) VALUES ({employee_id}, {date_str}, 8, 8, 8, 8, 8)")

    elif intent == 'submit_timesheet':
        if 'this week' in question:
            date_str = "{:%Y-%m-%d}".format(datetime.now())
        elif 'last week' in question:
            date_str = "{:%Y-%m-%d}".format(datetime.now() - timedelta(weeks=1))

        # Get the project code
        project_code = st.text_input('Project code')

        if day:
            # If day is found in the question, fill timesheet for that day
            hours = st.number_input(f'{day.capitalize()} hours', min_value=0, max_value=9)
            if st.button('Submit Timesheet'):
                c.execute("""
                    UPDATE timesheets SET {}_hours = ?
                    WHERE employee_id = ? AND week_ending = ?
                """.format(day), (hours, employee_id, date_str))

                st.write('Timesheet submitted successfully.')
                st.write(f'Total {day} hours: {hours}')

        else:
            # If no day is found in the question, fill timesheet for the whole week
            st.write('Please enter the hours you worked for each day of the week.')
            monday_hours = st.number_input('Monday hours', min_value=0, max_value=9)
            tuesday_hours = st.number_input('Tuesday hours', min_value=0, max_value=9)
            wednesday_hours = st.number_input('Wednesday hours', min_value=0, max_value=9)
            thursday_hours = st.number_input('Thursday hours', min_value=0, max_value=9)
            friday_hours = st.number_input('Friday hours', min_value=0, max_value=9)

            # Calculate total_daily_hours and total_weekly_hours
            total_daily_hours = max(monday_hours, tuesday_hours, wednesday_hours, thursday_hours, friday_hours)
            total_weekly_hours = monday_hours + tuesday_hours + wednesday_hours + thursday_hours + friday_hours

            if st.button('Submit Timesheet'):
                c.execute("""
                    INSERT INTO timesheets (
                        employee_id, week_ending, project_code, monday_hours, tuesday_hours, 
                        wednesday_hours, thursday_hours, friday_hours, total_daily_hours, total_weekly_hours
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (employee_id, date_str, project_code, monday_hours, tuesday_hours, 
                    wednesday_hours, thursday_hours, friday_hours, total_daily_hours, total_weekly_hours))
                
                conn.commit()

                st.write('Timesheet submitted successfully.')
                st.write(f'Total weekly hours: {total_weekly_hours}')

        return []



#--------------------------------------------------------------------------------------------------------------------------------------------------------

    elif intent == 'query_status':
        if date is None:
            print("Please specify a date for which you want to query the status.")
            return []
    
    # This part should not be inside the `if date is None` block.
        c.execute(f"SELECT total_weekly_hours FROM timesheets {condition} AND week_ending = '{date_str}'")
        result = c.fetchone()
        
        if result is None:
            print(f"No timesheet found for the week ending {date_str}.")
            return []
        else:
            total_weekly_hours = result[0]
            return [(f"Total weekly hours for the week ending {date_str}: {total_weekly_hours}",)]


#--------------------------------------------------------------------------------------------------------------------------------------------------------

    elif intent == 'edit_timesheet':
        day = get_day_from_text(question)  # Extract the day from the question
        if day:
            day_hours = f"{day}_hours"  # Create the column name for the specific day
            hours = st.number_input(f'{day.capitalize()} hours', min_value=0, max_value=9)
            # Update the hours for the specific day
            c.execute(f"UPDATE timesheets SET {day_hours} = {hours} {condition} {'' if condition == '' else 'AND'} week_ending = {date_str}")
        elif 'week' in question.lower():
            # If 'week' is found in the question, fill timesheet for the whole week
            project_code = st.text_input('Project code')
            st.write('Please enter the hours you worked for each day of the week.')
            monday_hours = st.number_input('Monday hours', min_value=0, max_value=9)
            tuesday_hours = st.number_input('Tuesday hours', min_value=0, max_value=9)
            wednesday_hours = st.number_input('Wednesday hours', min_value=0, max_value=9)
            thursday_hours = st.number_input('Thursday hours', min_value=0, max_value=9)
            friday_hours = st.number_input('Friday hours', min_value=0, max_value=9)

            # Display the week for which the timesheet is being filled
            week_ending = datetime.strptime(date_str.replace("'", ""), '%Y-%m-%d').strftime('%B %d, %Y')
            st.write(f'You are updating the timesheet for the week ending on {week_ending}.')

            if st.button('Submit Timesheet'):
                c.execute(f"""
                    UPDATE timesheets SET 
                    project_code = '{project_code}', 
                    monday_hours = {monday_hours}, 
                    tuesday_hours = {tuesday_hours}, 
                    wednesday_hours = {wednesday_hours}, 
                    thursday_hours = {thursday_hours}, 
                    friday_hours = {friday_hours}
                    {condition} AND week_ending = {date_str}
                """)

                conn.commit()
                
                st.write('Timesheet updated successfully.')

        else:
            print("Please specify the day or 'week' for which you want to edit the timesheet.")
            return []


#--------------------------------------------------------------------------------------------------------------------------------------------------------
        
    elif intent == 'get_holidays':
        c.execute("SELECT date, name FROM holidays")

#--------------------------------------------------------------------------------------------------------------------------------------------------------
        
    elif intent == 'auto_submit_timesheet':
        # Get the date of the current week
        current_week = get_nearest_friday()
        # Get the date of the next week
        next_week = current_week + timedelta(weeks=1)
        
        # Fetch the timesheet for the current week
        c.execute(f"SELECT * FROM timesheets {condition} AND week_ending = '{current_week.strftime('%Y-%m-%d')}'")
        current_week_timesheet = c.fetchone()
        
        if current_week_timesheet is not None:
            # If the current week's timesheet exists, duplicate it for the next week
            id, employee_id, _, project_code, monday_hours, tuesday_hours, wednesday_hours, thursday_hours, friday_hours, total_daily_hours, total_weekly_hours = current_week_timesheet
            c.execute(f"""
                INSERT INTO timesheets (
                    employee_id, week_ending, project_code, monday_hours, tuesday_hours, 
                    wednesday_hours, thursday_hours, friday_hours, total_daily_hours, total_weekly_hours
                ) 
                VALUES (
                    '{employee_id}', '{next_week.strftime('%Y-%m-%d')}', '{project_code}', {monday_hours}, {tuesday_hours}, 
                    {wednesday_hours}, {thursday_hours}, {friday_hours}, {total_daily_hours}, {total_weekly_hours}
                )
            """)
            st.write('Timesheet auto-submitted successfully.')
        else:
            st.write("No timesheet found for the current week. Please fill the timesheet manually.")
            return []


#--------------------------------------------------------------------------------------------------------------------------------------------------------

def generate_response(rows):
    if len(rows) == 0:
        return "No data found."
    else:
        # Create a DataFrame from the rows
        df = pd.DataFrame(rows, columns=['ID', 'Employee ID', 'Week Ending', 'Project Code', 'Monday Hours', 'Tuesday Hours', 'Wednesday Hours', 'Thursday Hours', 'Friday Hours', 'Total Daily Hours', 'Total Weekly Hours'])
        
        # Display the DataFrame
        st.write(df)




def chatbot(question, employee_id):  # role parameter removed
    intent = get_intent(question, pipeline)
    st.write(f"Recognized intent: {intent}")  # Display the recognized intent
    date = get_date_from_text(question)
    rows = execute_action(intent, date, question, employee_id)  # role removed from parameters

    if rows:
        generate_response(rows)



# Streamlit application
st.title('TIME-BOT 🤖')

employee_id = st.sidebar.text_input("Employee ID")
password = st.sidebar.text_input("Password", type="password")
# Implement a real login system
if employee_id and password:
    employee_id = login(employee_id, password)  # role removed
    if employee_id is None:
        st.sidebar.write("Invalid login credentials")
    else:
        question = st.text_input("Your question")
        if question:
            response = chatbot(question, employee_id)  # role removed from parameters
            st.write(response)
