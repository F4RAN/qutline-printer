import sqlite3
import os
defaults = ["orders", "receipts", "tables", "customer"]
"""
connection: 0: LAN, 1: Wi-Fi
type: 0: Orders, 1: Receipts, 2: Tables, 3: Customer
access_level: 0: Admin, 1: User
"""
def init_db():
# Check if the database file exists, and create it if it doesn't
    if not os.path.exists('dbs/database.sqlite'):
        conn = sqlite3.connect('dbs/database.sqlite')
        cursor = conn.cursor()

        # Create the Printer table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Printer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                connection INTEGER,
                mac_addr TEXT,
                ip_addr TEXT,
                access_level INTEGER,
                is_static_ip BOOLEAN DEFAULT 0,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create the Job table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Job (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type INTEGER,
                printer_id INTEGER NOT NULL,
                FOREIGN KEY (printer_id) REFERENCES Printer (id)
            )
        ''')

        # Create the WifiCredential table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS WifiCredential (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ssid TEXT,
                password TEXT
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
    else:
        print("The database file already exists.")
