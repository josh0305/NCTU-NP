import sqlite3

conn = sqlite3.connect('NP.db')
db = conn.cursor()

db.execute('''CREATE TABLE User(uid CHAR(50) PRIMARY KEY 	NOT NULL, pwd TEXT 	NOT NULL, token TEXT );''')
db.execute('''CREATE TABLE Invite(send_id CHAR(50)  NOT NULL, recv_id CHAR(50) NOT NULL);''')
db.execute('''CREATE TABLE Friendship(uid CHAR(50)  NOT NULL, fid CHAR(50) NOT NULL);''')
db.execute('''CREATE TABLE Post(uid CHAR(50) NOT NULL, msg TEXT);''')