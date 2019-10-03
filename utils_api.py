import requests
import sqlite3
from sqlite3 import Error

def create_connection(db_file='LibraryBot.db'):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_db():
    create_table_sql = """CREATE TABLE IF NOT EXISTS UserData (
        user_id TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        password TEXT NOT NULL
        );"""
    conn = create_connection()
    if conn is not None:
        create_table(conn, create_table_sql)
        return True
    else:
        print("Error! cannot create the database connection.")
        return False


def register_user(username, email, password, phone):
    data = {"name":username, "email":email, "password":password, "phone_no":phone}
    reg = requests.post('http://18.223.160.194/Laundry/api/ebregister', data=data)
    return reg.json()

def delete_logged_in(conn, user_id):
    sql = """DELETE FROM UserData WHERE user_id={}""".format(user_id)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def login_user(email, password):
    data = {"email":email, "password":password}
    login = requests.post('http://18.223.160.194/Laundry/api/eblogin', data=data)
    return login.json()

def check_logged_in(conn, user_id):
    sql = """SELECT email, password FROM UserData WHERE user_id='{}'""".format(user_id)
    conn.execute(sql)
    fetched = conn.fetchall()
    if fetched != []:
        email = fetched[0][0]
        password = fetched[0][1]
        logged_in = login_user(email, password)
        return logged_in
    else:
        return []

def insert_logged_in(conn, user_id, email, password):
    sql = """INSERT INTO UserData (user_id, email, password) VALUES ({0}, {1}, {2})""".format(user_id,email, password)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def homelisting():
    book_list = requests.post('http://18.223.160.194/Laundry/api/homelisting')
    return book_list.json()

    

