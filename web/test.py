import sqlite3

conn = sqlite3.connect('bhoomi.db')
c = conn.cursor()

# Add missing columns
try:
    c.execute("ALTER TABLE crops ADD COLUMN stage TEXT DEFAULT 'Vegetative'")
    c.execute("ALTER TABLE crops ADD COLUMN progress INTEGER DEFAULT 0")
    print("Columns added successfully.")
except Exception as e:
    print("Error:", e)

conn.commit()
conn.close()
