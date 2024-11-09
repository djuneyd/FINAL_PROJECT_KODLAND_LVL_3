import sqlite3
from config import DATABASE

class User_vacancies_manger:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            # creating a table for keeping users, their their id, telegram id, username
            conn.execute('''CREATE TABLE IF NOT EXISTS users
                             (id INTEGER PRIMARY KEY, telegram_id INTEGER, username TEXT)''')
            # creating a table for keeping vacancies, their id, user_id from users table, description
            conn.execute('''CREATE TABLE IF NOT EXISTS vacancies
                             (id INTEGER PRIMARY KEY, user_id INTEGER, description TEXT, FOREIGN KEY(user_id) REFERENCES users(id))''')
            
    def executemany(self, sql, data = tuple()): # function for executing SQL commands
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    
    def select_data(self, sql, data = tuple()): # fuction for fetching data from database
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()


if __name__ == '__main__':
    #user_vacancies_manager = User_vacancies_manger(DATABASE)
    #user_vacancies_manager.create_tables()
    

    # create extra column for vacancies table called name
    conn = sqlite3.connect(DATABASE)
    with conn:
       conn.execute('''ALTER TABLE vacancies ADD COLUMN name TEXT''')
    conn.close()