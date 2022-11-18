import mysql.connector

mydb = mysql.connector.connect(
  host="mysqldb",
  user="martim",
  password="Martim123",
  port=100
)

print(mydb)