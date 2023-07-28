import sqlite3
conn = sqlite3.connect('timesheets.db')

c = conn.cursor()

c.execute("SELECT * FROM timesheets")
print(c.fetchall())