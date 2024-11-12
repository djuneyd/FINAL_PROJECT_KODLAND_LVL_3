import sqlite3
from config import ADVICE_DATABASE

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

class Advices_database:
    def __init__(self, database):
        self.database = database

    def select_data(self, sql, data = tuple()): # fuction for fetching data from database
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
        
    def random_advice(self):
        sql = 'SELECT text FROM advice ORDER BY random() LIMIT 1'
        return self.select_data(sql)[0][0]

if __name__ == '__main__':
    pass