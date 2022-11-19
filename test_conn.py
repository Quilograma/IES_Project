import mysql.connector

mydb = mysql.connector.connect(
  host="mysqldb",
  user="martim",
  password="Martim123"
)

print(mydb)