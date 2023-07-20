import sqlite3
conn = sqlite3.connect('timesheets.db')

c = conn.cursor()

c.execute("SELECT * FROM timesheets WHERE employee_id=? AND week_ending=?", ('123', '2023-02-10'))
print(c.fetchall())