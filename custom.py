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

def prettyTimeDelta(seconds):
  seconds = int(seconds)
  days, seconds = divmod(seconds, 86400)
  hours, seconds = divmod(seconds, 3600)
  minutes, seconds = divmod(seconds, 60)
  if days > 0:
      return '%dd %dh' % (days, hours)
  elif hours > 0:
      return '%dh %dm' % (hours, minutes)
  elif minutes > 0:
      return '%dm %ds' % (minutes, seconds)
  else:
      return '%ds' % (seconds,)

class bot(ch.RoomManager):
  _lastFoundBlockNum = 0
  _lastFoundBlockLuck = 0
  _lastFoundBlockValue = 0
  _lastFoundBlockTime = 0
  NblocksNum = 0
  NblocksAvg = 0
  Nvalids = 0

  def onInit(self):
    self.setNameColor("CC6600")
    self.setFontColor("000000")
    self.setFontFace("0")
    self.setFontSize(11)

  def onConnect(self, room):
    print("Connected")
     
  def onReconnect(self, room):
    print("Reconnected")
     
  def onDisconnect(self, room):
    print("Disconnected")
    for room in self.rooms:
      room.reconnect()
    room.message("Warning: self-destruction cancelled. Systems online")

  def onMessage(self, room, user, message):

    if self.user == user: return

    try: 
      cmds = ['/triteregister', '/triteremove', '/tritelog', '/tritereport', '/trite', '/tritequeue']
      hlps = ['?triteregister', '?triteremove', '?tritelog', '?tritereport', '?trite', '?tritequeue']
      searchObj = re.findall(r'(\/\w+)(\.\w+)?|(\?\w+)', message.body, re.I)
      searchObjCmd = []
      searchObjArg = []
      searchObjArg2 = []
      searchObjHlp = []
      for i in range(len(searchObj)):
        for j in range(len(cmds)):
          if searchObj[i][0] == cmds[j]:
            searchObjCmd.append(searchObj[i][0])
            searchObjArg.append(searchObj[i][1])
            #searchObjArg2.append(searchObj[i][2])
        if searchObj[i][2]:
          searchObjHlp.append(searchObj[i][2])
      command = searchObjCmd
      argument = searchObjArg
      #argument2 = searchObjArg2
      helper = searchObjHlp
    except:
      room.message("I dont know what to do. ".format(user.name))

    for i in range(len(helper)):
      hlp = helper[i]
      if hlp in hlps:
        hlp = hlp[1:]

        if hlp.lower() == "triteregister":
            room.message("Usage (/command): triteregister.wallet. Register your chatango username with your wallet address.")

        if hlp.lower() == "triteremove":
            room.message("Usage (/command): triteremove. Removes your user, including data.")

        if hlp.lower() == "tritelog":
            room.message("Usage (/command): tritelog. Saves time and shares into log.")

        if hlp.lower() == "tritereport":
            room.message("Usage (/command): tritereport. (thinking of implementing email). Sends a PM to you with a link to graph of your logged stats.")

        if hlp.lower() == "tritequeue":
            room.message("Usage (/command): tritequeue. Shows list of users in queue currently doing measurements.")

        if hlp.lower() == "trite":
            room.message("Usage (/command): (?command). / executes commands and ? explains commands.")
            
    for i in range(len(command)):
      cmd = command[i]
      arg = argument[i]
      #arg2 = argument2[i]
      cmd = cmd[1:]
      arg = arg[1:]
      #arg2 = arg2[1:]

      try:
        
        if cmd.lower() == "triteregister":
          if str(arg) == "":
            room.message("No.")
            break
          chatango_nick = user.name
          pattern = re.compile("^(Anon[0-9]+)")
          if pattern.match(chatango_nick):
            room.message("Please log in to Chatango before trying to register with me.")
            break
          db=MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("SELECT EXISTS(SELECT name FROM users WHERE name='" + chatango_nick + "')")
          output=cursor.fetchone()
          #print(str(output[0]), "Check name against chatango_nick")
          #cursor.close()
          if output[0] == 1:
            room.message("You already have an account.")
            #print(str("already exists"))
          elif output[0] == 0:
            db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
            cursor = db.cursor()
            #print(str("Trying to INSERT INTO db."))
            cursor.execute("INSERT INTO users (name, wallet) VALUES ('" + chatango_nick + "', '" + arg + "')")
            db.commit()
            room.message("You have been registered.")
            #cursor.close()
          #print(str(chatango_nick), str(arg))
          cursor.close()

        if cmd.lower() == "triteremove":
          chatango_nick = user.name
          pattern = re.compile("^(Anon[0-9]+)")
          if pattern.match(chatango_nick):
            room.message("Please log in to Chatango before trying to register with me.")
            break
          db=MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("SELECT id FROM users WHERE name='" + chatango_nick + "'")
          output=cursor.fetchone()
          id=output[0]
          cursor.close()
          db=MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("DELETE FROM data WHERE uid='" + str(id) + "'")
          db.commit()
          cursor.close()
          db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("DELETE FROM users WHERE name='" + chatango_nick + "'")
          db.commit()
          room.message("Your user has been removed.")
          cursor.close()

        if cmd.lower() == "tritelog":
          chatango_nick = user.name
          db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("SELECT EXISTS(SELECT name FROM users WHERE name='" + chatango_nick + "')")
          output = cursor.fetchone()
          #print(str(output[0]), "Check name against chatango_nick")
          if output[0] == 1:
            cursor.close()
            db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
            cursor = db.cursor()
            cursor.execute("SELECT id FROM users WHERE name='" + chatango_nick + "'")
            output = cursor.fetchone()
            userID=output[0]
            #print(str(userID))
            cursor.close()
            #sanity check queue
            db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
            cursor = db.cursor()
            cursor.execute("SELECT count FROM queue WHERE uid='" + str(userID) + "'")
            output = cursor.fetchone()
            #cursor.close()
            if output:
              cursor.close()
              room.message("You already have a job in the queue, please wait for that to finish before you put another job in.")
              break
            cursor.close()
            #time = datetime.now()
            #time = time.strftime('%Y-%m-%d %H:%M:%S')
            #db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
            #cursor = db.cursor()
            #cursor.execute("SELECT wallet FROM users WHERE name='" + chatango_nick + "'")
            #output = cursor.fetchone()
            #wallet= str(output[0])
            #xmrWalletAPI = requests.get(apiUrlXMR + "miner/" + wallet + "/stats").json()
            #shares = xmrWalletAPI['validShares']
            #print(str(shares), str(wallet))
            #cursor.close()
            #QUEUE
            db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
            cursor = db.cursor()
            cursor.execute("INSERT INTO queue (uid, count) VALUES ('" + str(userID) + "', '" + str(5) + "')")
            db.commit()
            room.message("A job for logging your shares over time has been written into the queue. Please check your result with tritelog-command when your measurements are done. At present this is 6 measurements each hour (6 hours, duh).")
            #OLD NO Q
            #db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
            #cursor = db.cursor()
            #cursor.execute("INSERT INTO data (uid, shares, time) VALUES ('" + str(userID) + "', '" + str(shares) + "', '" + str(time) + "')")
            #db.commit()
            #room.message("Logged shares and time.")
          elif output[0] == 0:
            room.message("You are not registered.")
          cursor.close()

        if cmd.lower() == "tritereport":
          chatango_nick = user.name
          db=MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          try:
            cursor.execute("SELECT id FROM users WHERE name='" + chatango_nick + "'")
          except:
            room.message("It seems you are not registered.")
            break
          output=cursor.fetchone()
          try:
            uid=output[0]
          except:
            room.message("It seems you are not registered.")
            break
          cursor.close()
          db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor = db.cursor()
          cursor.execute("SELECT * FROM data WHERE uid='" + str(uid) + "'")
          #msg = [] 
          #msg.append("Showing logged shares for @" + chatango_nick + ":")
          excelFileSQL=cursor.fetchall()
          excelFile=''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
          #for row in cursor.fetchall():
          #  msg.append("ID: " + str(row[1]) + " Shares: " + str(row[2]) + " Time: " + str(row[3]))
          #else:
          #  room.message("You must construct additional msg.")
          #message = ''.join(msg)
          message = str(excelFile)
          #cursor.close()
          workbookPath = "/home/trite/trite2k2/excel/"
          workbook = xlsxwriter.Workbook(workbookPath + message + '.xlsx', {'strings_to_numbers': True})
          worksheet = workbook.add_worksheet()
          bold = workbook.add_format({'bold': 1})
          # Add the worksheet data that the charts will refer to.
          headings = ['ID', 'Shares', 'Time']
          data=excelFileSQL
          worksheet.write_row('A1', headings, bold)
          i=1
          for row in data:
            ID=str(row[1])#.replace("'", "")
            SHARES=str(row[2])#.replace("'", "")
            TIME=str(row[3])#.replace("'", "")
            #print(str(ID), str(SHARES), str(TIME))
            worksheet.write(i, 0, ID)
            worksheet.write(i, 1, SHARES)
            worksheet.write(i, 2, TIME)
            i=int(i+1)
          # Create a new chart object. In this case an embedded chart.
          chart1 = workbook.add_chart({'type': 'line'})
          # Configure the first series.
          chart1.add_series({
            'name': '=Sheet1!$B$1',
            'categories': '=Sheet1!$C$2:$C$' + str(i),
            'values': '=Sheet1!$B$2:$B$' + str(i),
          })
          # Configure second series. Note use of alternative syntax to define ranges.
          chart1.add_series({
            'name': '=Sheet1!$C$1',
            'categories': '=Sheet1!$B$2:$B$' + str(i),
            'values': '=Sheet1!$C$2:$C$' + str(i),
          })
          # Add a chart title and some axis labels.
          chart1.set_title({'name': 'Share Log Report'})
          chart1.set_x_axis({'name': 'Time'})
          chart1.set_y_axis({'name': 'Shares'})
          # Set an Excel chart style. Colors with white outline and shadow.
          chart1.set_style(2)
          # Insert the chart into the worksheet (with an offset).
          worksheet.insert_chart('D2', chart1, {'x_offset': 50, 'y_offset': 50})
          workbook.close()
          whisper = str("foderus.se/excel/") + message + str(".xlsx")
          self.pm.message(ch.RoomManager(chatango_nick), whisper)

        if cmd.lower() == "tritequeue":
          db = MySQLdb.connect(host="localhost", user="custompython", passwd="", db="custompython")
          cursor=db.cursor()
          cursor.execute("SELECT * FROM queue")
          countArray = cursor.fetchall()
          cursor.close()
          userList = ""
          for i in countArray:
            cursor=db.cursor()
            cursor.execute("SELECT name FROM users WHERE id='" + str(i[0]) + "'")
            output = cursor.fetchone()
            output = output[0]
            userList = userList + str(output) + "\n"
            cursor.close()
          room.message("There are currently " + str(len(countArray)) + " jobs in queue for: " + "\n" + str(userList))

        if cmd.lower() == "trite":
          room.message("Commands (?,/): trite, triteregister, tritelog, triteremove, tritereport. Use ?<command> to explain a command.")


      except json.decoder.JSONDecodeError:
        print("There was a json.decoder.JSONDecodeError while attempting /" + str(cmd.lower()) + " (probably due to /pool/stats/)")
        room.message("JSON Bourne is trying to kill me!")
      #except:
      #  print("Error while attempting /" + str(cmd.lower()))
      #  room.message("Main Cmd/Msg Function Except.")

rooms = ["supportxmr"]
username = "trite2k2"
password = ""

try:
  bot.easy_start(rooms,username,password)
except KeyboardInterrupt:
  print("\nStopped")
