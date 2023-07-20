import sqlite3


def get_all_table_structures(database_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    # Get the names of all tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()

    table_structures = {}
    for table in tables:
        table_name = table[0]
        
        # Get the structure of the table
        c.execute(f"PRAGMA table_info({table_name})")
        table_structure = c.fetchall()

        # Add the structure to the dictionary
        table_structures[table_name] = table_structure

    conn.close()

    return table_structures

table_structures = get_all_table_structures('timesheets.db')
for table_name, table_structure in table_structures.items():
    print(f"Structure of {table_name}:")
    for column_info in table_structure:
        print(column_info)
    print()
