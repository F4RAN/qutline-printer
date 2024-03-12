import sqlite3
DATABASE = "dbs/database.sqlite"
# stores = cursor.execute("SELECT * FROM Job").fetchall()

def get_db():
    db = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    return cursor
cursor = get_db()
cursor.execute("INSERT INTO Printer (name, mac_addr, ip_addr, access_level, connection) VALUES (?,?,?,?,?)",
                   ("Test", "0C:7F:ED:C0:E0:4C", "192.168.1.159", 0, 1))
