import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create a table to store user accounts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
