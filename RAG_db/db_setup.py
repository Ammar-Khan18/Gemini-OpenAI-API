# # setup_db.py
# import sqlite3

# # Create a new database file (or open if exists)
# conn = sqlite3.connect("data.db")
# cursor = conn.cursor()

# # Create a table for example (you can change this schema)
# cursor.execute("""
# CREATE TABLE employees (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     department TEXT NOT NULL,
#     role TEXT NOT NULL
# )
# """)

# # Insert sample rows
# cursor.executemany("""
# INSERT INTO employees (name, department, role)
# VALUES (?, ?, ?)
# """, [
#     ("Ammar Khan", "Engineering", "Software Engineer"),
#     ("Sara Malik", "HR", "Recruitment Specialist"),
#     ("Ali Raza", "Engineering", "Data Scientist"),
#     ("Fatima Noor", "Marketing", "Content Strategist")
# ])

# # Save changes & close
# conn.commit()
# conn.close()

# print("✅ Database created: data.db with 'employees' table.")
###################################
# For Verification of DB
import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM employees")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
######################################
