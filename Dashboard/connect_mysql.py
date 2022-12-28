import mysql.connector

conn = mysql.connector.connect(user='martim', password='Martim123',
                              host='mysqldb',
                              database='projectdb')

cursor = conn.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS users 
    ( 
        username VARCHAR(30),
        password VARCHAR(100),
        PRIMARY KEY(username)
    );
    '''
)