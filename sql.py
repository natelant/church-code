import sqlite3

conn = sqlite3.connect('db_scriptures.db')  # Replace with your actual file
cursor = conn.cursor()

cursor.execute("""
    UPDATE verses
    SET book = chapter
    WHERE volume = 'Doctrine & Covenants';
""")

conn.commit()
print(f"Rows updated: {cursor.rowcount}")

cursor.execute("""
    SELECT * FROM verses WHERE volume = 'Doctrine & Covenants';
""")
rows = cursor.fetchall()
print(f"Matching rows: {len(rows)}")

conn.close()