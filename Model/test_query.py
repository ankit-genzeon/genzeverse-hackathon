import sqlite3

conn = sqlite3.connect('timesheets.db')
c = conn.cursor()

date_str = '2023-02-10'  # Replace with the date you're interested in
c.execute(f"SELECT * FROM timesheets WHERE week_ending = '{date_str}' AND employee_id = 123")
result_date = c.fetchall()
print(f"Results for date {date_str}:\n{result_date}\n")

month_str = '2023-02'  # Replace with the month you're interested in
c.execute(f"SELECT * FROM timesheets WHERE strftime('%Y-%m', week_ending) = '{month_str}' AND employee_id = 123")
result_month = c.fetchall()
print(f"Results for month {month_str}:\n{result_month}\n")

year_str = '2023'  # Replace with the year you're interested in
c.execute(f"SELECT * FROM timesheets WHERE strftime('%Y', week_ending) = '{year_str}' AND employee_id = 123")
result_year = c.fetchall()
print(f"Results for year {year_str}:\n{result_year}\n")

project_code = 'A123'  # Replace with the project code you're interested in
c.execute(f"SELECT * FROM timesheets WHERE project_code = '{project_code}' AND employee_id = 123")
result_project = c.fetchall()
print(f"Results for project {project_code}:\n{result_project}\n")

conn.close()
