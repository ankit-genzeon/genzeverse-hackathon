import sqlite3
conn = sqlite3.connect('timesheets.db')

c = conn.cursor()

c.execute('''
          CREATE TABLE timesheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            employee_id VARCHAR(50) NOT NULL,
            week_ending DATE NOT NULL,
            project_code VARCHAR(20) NOT NULL,
            monday_hours INTEGER CHECK(monday_hours <= 9),
            tuesday_hours INTEGER CHECK(tuesday_hours <= 9),
            wednesday_hours INTEGER CHECK(wednesday_hours <= 9),
            thursday_hours INTEGER CHECK(thursday_hours <= 9),
            friday_hours INTEGER CHECK(friday_hours <= 9),
            total_daily_hours INTEGER CHECK(total_daily_hours <= 9),
            total_weekly_hours INTEGER CHECK(total_weekly_hours <= 45),
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
          )
          ''')

# Create employees table
c.execute('''
          CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            employee_id VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(128) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'Employee',
            manager_id VARCHAR(50),
            FOREIGN KEY(manager_id) REFERENCES employees(employee_id)
          )
          ''')



# Create notifications table
c.execute('''
          CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id VARCHAR(50) NOT NULL,
            week_ending DATE NOT NULL,
            hours_worked INTEGER NOT NULL,
            status VARCHAR(20) NOT NULL CHECK(status in ('Unread', 'Read')),
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
          )
          ''')

c.execute('''
          CREATE TABLE holidays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            name VARCHAR(50)
          )
          ''')

conn.commit()
