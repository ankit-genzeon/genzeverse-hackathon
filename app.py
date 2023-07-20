import sqlite3
import datefinder
from getpass import getpass
from werkzeug.security import check_password_hash
import streamlit as st
import joblib

# Load the model from the file
pipeline = joblib.load('intent_recognition_model.pkl')

conn = sqlite3.connect('timesheets.db')
c = conn.cursor()

def login(employee_id, password):

    c.execute(
        f"SELECT password_hash, role FROM employees WHERE employee_id = '{employee_id}'")
    result = c.fetchone()

    if result is None:
        return None, None

    password_hash, role = result

    if not check_password_hash(password_hash, password):
        return None, None

    return employee_id, role

def get_date(question):
    matches = datefinder.find_dates(question)
    for match in matches:
        return match
    return None
    
question = "What was my timesheet for February 10, 2023?"
print(get_date(question))

def get_intent(question, model):
    return model.predict([question])[0]

def execute_action(intent, date=None, question=None, employee_id=None, role=None):  # add question as a parameter

    date = get_date(question)

    if date is None:
        print("Could not find a relative date in your question. Please specify a time frame.")
        return []
    date_str = date.strftime("'%Y-%m-%d'")

    if employee_id is not None:
        employee_id = f"'{employee_id}'"

    if role == 'Employee':
        condition = f"WHERE employee_id = {employee_id}"
    elif role == 'Manager':
        condition = ""
    else:
        condition = "WHERE 1 = 0"

    if intent == 'get_past_timesheet':
        if 'week' in question:
            c.execute(f"SELECT * FROM timesheets {condition} AND week_ending < {date_str}")
        elif 'month' in question:
            c.execute(f"SELECT * FROM timesheets {condition} AND strftime('%Y-%m', week_ending) = strftime('%Y-%m', {date_str})")
        elif 'quarter' in question:
            c.execute(f"SELECT * FROM timesheets {condition} AND strftime('%Y', week_ending) = strftime('%Y', {date_str}) AND ((strftime('%m', week_ending) + 2) / 3) = ((strftime('%m', {date_str}) + 2) / 3)")
        else:  # year or other
            c.execute(f"SELECT * FROM timesheets {condition} AND strftime('%Y', week_ending) = strftime('%Y', '{date_str}')")

#--------------------------------------------------------------------------------------------------------------------------------------------------------

    # elif intent == 'submit_timesheet':
    #     # Assuming 8 hours for each weekday
    #     c.execute(f"INSERT INTO timesheets (employee_id, week_ending, monday_hours, tuesday_hours, wednesday_hours, thursday_hours, friday_hours) VALUES ({employee_id}, {date_str}, 8, 8, 8, 8, 8)")
elif intent == 'submit_timesheet':
    if 'this week' in question:
        date_str = "'{:%Y-%m-%d}'".format(datetime.now())
    elif 'last week' in question:
        date_str = "'{:%Y-%m-%d}'".format(datetime.now() - timedelta(weeks=1))

    # Get the hours from the user
    st.write('Please enter the hours you worked for each day of the week.')
    monday_hours = st.number_input('Monday hours', min_value=0, max_value=9)
    tuesday_hours = st.number_input('Tuesday hours', min_value=0, max_value=9)
    wednesday_hours = st.number_input('Wednesday hours', min_value=0, max_value=9)
    thursday_hours = st.number_input('Thursday hours', min_value=0, max_value=9)
    friday_hours = st.number_input('Friday hours', min_value=0, max_value=9)
    
    # Get the project code
    project_code = st.text_input('Project code')

    # Calculate total_daily_hours and total_weekly_hours
    total_daily_hours = max(monday_hours, tuesday_hours, wednesday_hours, thursday_hours, friday_hours)
    total_weekly_hours = monday_hours + tuesday_hours + wednesday_hours + thursday_hours + friday_hours

    if st.button('Submit Timesheet'):
        c.execute(f"""
            INSERT INTO timesheets (
                employee_id, week_ending, project_code, monday_hours, tuesday_hours, 
                wednesday_hours, thursday_hours, friday_hours, total_daily_hours, total_weekly_hours
            ) 
            VALUES (
                {employee_id}, {date_str}, '{project_code}', {monday_hours}, {tuesday_hours}, 
                {wednesday_hours}, {thursday_hours}, {friday_hours}, {total_daily_hours}, {total_weekly_hours}
            )
        """)

        st.write('Timesheet submitted successfully.')
        st.write(f'Total weekly hours: {total_weekly_hours}')
    return []


    # ... rest of your function ...


#--------------------------------------------------------------------------------------------------------------------------------------------------------

    elif intent == 'query_status':
        if date is None:
            print("Please specify a date for which you want to query the status.")
            return []
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
        # Assuming the timesheet is edited to 8 hours for each weekday
        c.execute(f"UPDATE timesheets SET monday_hours = 8, tuesday_hours = 8, wednesday_hours = 8, thursday_hours = 8, friday_hours = 8 {condition} {'' if condition == '' else 'AND'} week_ending = '{date_str}'")

#--------------------------------------------------------------------------------------------------------------------------------------------------------
        
    elif intent == 'get_holidays':
        c.execute("SELECT date, name FROM holidays")

#--------------------------------------------------------------------------------------------------------------------------------------------------------
        
    elif intent == 'auto_submit_timesheet':
        c.execute(f"SELECT * FROM timesheets {condition} ORDER BY week_ending DESC LIMIT 1")
        last_week_timesheet = c.fetchone()
        if last_week_timesheet is not None:
            monday_hours = last_week_timesheet[3]
            tuesday_hours = last_week_timesheet[4]
            wednesday_hours = last_week_timesheet[5]
            thursday_hours = last_week_timesheet[6]
            friday_hours = last_week_timesheet[7]
            c.execute(f"INSERT INTO timesheets (employee_id, week_ending, monday_hours, tuesday_hours, wednesday_hours, thursday_hours, friday_hours) VALUES ({employee_id}, {date_str}, {monday_hours}, {tuesday_hours}, {wednesday_hours}, {thursday_hours}, {friday_hours})")
        else:
            print("No timesheet from last week found. Please fill the timesheet manually.")
            return []
    else:
        print(f"Intent {intent} not recognized.")
        return []

    rows = c.fetchall()
    conn.close()
    return rows

#--------------------------------------------------------------------------------------------------------------------------------------------------------


def generate_response(rows):
    if len(rows) == 0:
        return "No data found."
    else:
        # This is a basic implementation that simply joins the rows into a string
        # You might want to customize this to format the response in a way that's suitable for your application
        return "\n".join(str(row) for row in rows)


def chatbot(question, employee_id, role):
    intent = get_intent(question, pipeline)
    st.write(f"Recognized intent: {intent}")  # Display the recognized intent
    date = get_date(question)
    rows = execute_action(intent, date, question, employee_id, role)  # pass question to execute_action()
    response = generate_response(rows)
    return response



# Streamlit application
st.title('Chatbot')

employee_id = st.sidebar.text_input("Employee ID")
password = st.sidebar.text_input("Password", type="password")
# Implement a real login system
if employee_id and password:
    employee_id, role = login(employee_id, password)
    if employee_id is None:
        st.sidebar.write("Invalid login credentials")
    else:
        question = st.text_input("Your question")
        if question:
            response = chatbot(question, employee_id, role)
            st.write(response)
