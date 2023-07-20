import sqlite3
conn = sqlite3.connect('timesheets.db')

c = conn.cursor()

c.execute('''
          CREATE TRIGGER notify_manager
          AFTER INSERT ON timesheets
          WHEN NEW.total_weekly_hours < 45
          BEGIN
            INSERT INTO notifications (employee_id, week_ending, hours_worked, status)
            VALUES (NEW.employee_id, NEW.week_ending, NEW.total_weekly_hours, 'Unread');
          END;
          ''')
