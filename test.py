#!/usr/bin/python3
import MySQLdb
from time import sleep

db=MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")

cursor=db.cursor()
#table="users"
#cursor.execute("SELECT * FROM " + table)
#cursor.execute("INSERT INTO users (name, wallet) VALUES ('trite', 'wallet')")
#msg=cursor.fetchone()
#print(str(msg[2]))
#db.commit()

cursor.execute("SELECT * FROM queue")
output = cursor.fetchall()
print("There are currently " + str(len(output)) + " jobs in queue for: ")
cursor.close()

userList = ""

for i in output:
  cursor=db.cursor()
  cursor.execute("SELECT name FROM users WHERE id='" + str(i[0]) + "'")
  output = cursor.fetchone()
  output = output[0]
  userList = userList + str(output) + "\n"
  cursor.close()
print(str(userList))
