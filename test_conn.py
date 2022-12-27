import mysql.connector

mydb = mysql.connector.connect(
  host="mysqldb",
  user="martim",
  database='projectdb',
  password="Martim123"
)

print(mydb)