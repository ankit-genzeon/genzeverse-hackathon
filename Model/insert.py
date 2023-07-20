import sqlite3
conn = sqlite3.connect('timesheets.db')

c = conn.cursor()

from werkzeug.security import generate_password_hash

employees = [
    ('123', generate_password_hash('password123'), 'Employee'),
    ('124', generate_password_hash('password124'), 'Employee'),
    ('125', generate_password_hash('password125'), 'Manager'),
    ('126', generate_password_hash('password126'), 'Employee'),
    ('127', generate_password_hash('password127'), 'Manager')
]

c.executemany("INSERT INTO employees (employee_id, password_hash, role) VALUES (?, ?, ?)", employees)

timesheets = [
    ('123', '2023-02-10', 'A123', 8, 8, 8, 8, 8, 40),
    ('124', '2023-02-10', 'B234', 9, 9, 9, 9, 9, 45),
    ('125', '2023-02-10', 'C345', 9, 9, 9, 9, 7, 43),
    ('126', '2023-02-10', 'D456', 9, 9, 9, 9, 8, 44),
    ('127', '2023-02-10', 'E567', 8, 8, 8, 8, 9, 41),
    ('123', '2023-02-17', 'F678', 9, 9, 9, 9, 8, 44),
    ('124', '2023-02-17', 'G789', 8, 8, 8, 8, 9, 41),
    ('125', '2023-02-17', 'H890', 9, 9, 9, 9, 9, 45),
    ('126', '2023-02-17', 'I901', 9, 9, 9, 9, 8, 44),
    ('127', '2023-02-17', 'J012', 8, 8, 8, 8, 9, 41)
]    

c.executemany("INSERT INTO timesheets (employee_id, week_ending, project_code, monday_hours, tuesday_hours, wednesday_hours, thursday_hours, friday_hours, total_weekly_hours) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", timesheets)


c.execute("""INSERT INTO holidays (date, name) VALUES
('2023-01-26', 'Republic Day'),
('2023-08-15', 'Independence Day'),
('2023-10-02', 'Gandhi Jayanti'),
('2023-05-26', 'Eid ul-Fitr'),
('2023-08-22', 'Raksha Bandhan'),
('2023-10-25', 'Diwali'),
('2023-11-24', 'Guru Nanak Jayanti'),
('2023-12-25', 'Christmas Day')""")


conn.commit()
conn.close()
