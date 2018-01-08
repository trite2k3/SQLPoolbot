#!/usr/bin/python3
import json
import re
from datetime import datetime
import requests
import subprocess
import smtplib
import xlsxwriter
import MySQLdb
import ch
import random
import string

apiUrlXMR = "https://supportxmr.com/api/"

db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
cursor = db.cursor()
cursor.execute("SELECT * FROM queue")
output = cursor.fetchall()
cursor.close()
#
# 0 = UserID
# 1 = Count
#
#for i in output:
#  print(str(i[0]), str(i[1]))
for i in output:
  db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
  cursor = db.cursor()
  cursor.execute("SELECT wallet FROM users WHERE id='" + i[0] + "'")
  walletSQL = cursor.fetchone()
  wallet = str(walletSQL[0])
  cursor.close()
  time = datetime.now()
  time = time.strftime('%Y-%m-%d %H:%M:%S')
  xmrWalletAPI = requests.get(apiUrlXMR + "miner/" + wallet + "/stats").json()
  shares = xmrWalletAPI['validShares']
  db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
  cursor = db.cursor()
  cursor.execute("INSERT INTO data (uid, shares, time) VALUES ('" + str(i[0]) + "', '" + str(shares) + "', '" + str(time) + "')")
  db.commit()
  cursor.close()
  db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
  cursor = db.cursor()
  if i[1] == 0:
    cursor.execute("DELETE FROM queue WHERE uid='" + i[0] + "'")
  else:
    cursor.execute("DELETE FROM queue WHERE uid='" + i[0] + "'")
    recount = int(i[1] - 1)
    cursor.execute("INSERT INTO queue (uid, count) VALUES ('" + str(i[0]) + "', '" + str(recount) + "')")
  db.commit()
  cursor.close()
