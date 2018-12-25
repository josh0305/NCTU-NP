import sqlite3
import socket 
import json
import uuid
import sys

#Database connect

conn = sqlite3.connect('NP.db')
db = conn.cursor()

#-----------------------------------Function------------------------------------------------------------------------

#validation
def validation_token(token):
	user = db.execute("SELECT uid, token from User Where token = ?", (token,)).fetchall()
	if(len(user) > 0):
		return True
	else:
		return False

def validation_account(uid, pwd):
	user = db.execute("SELECT uid, pwd from User where uid = ? and pwd = ? ", [uid, pwd]).fetchall()
	if(len(user) > 0):
		return True
	else:
		return False

#check
def existence(uid):
	user = db.execute("SELECT uid from User Where uid = ?" ,(uid,)).fetchall()
	if(len(user) > 0):
		return True
	else:
		return False

def check_fship(uid, fid):
	ship = db.execute("SELECT uid from Friendship where uid = ? and fid = ?", [uid, fid]).fetchall()
	if(len(ship) > 0):
		return True
	else:
		return False

def check_invite(send, recv):
	inv = db.execute("SELECT send_id from Invite where send_id = ? and recv_id = ?" ,[send, recv]).fetchall()
	if(len(inv) > 0):
		return True
	else:
		return False

#fetch something about token and uid
def newtoken():
	return str(uuid.uuid1())

def fetch_token(uid):
	user = db.execute("SELECT token from User where uid = ?", (uid,)).fetchall()
	return user[0][0]

def fetch_uid(token):
	user = db.execute("SELECT uid from User where token = ?", (token,)).fetchall()
	return user[0][0]

def fetch_invited(uid):
	inv = db.execute("SELECT send_id from Invite where recv_id = ?", (uid,))
	l = [row[0] for row in inv]
	return l

def fetch_friend(uid):
	fri = db.execute("SELECT fid from Friendship where uid = ?", (uid,))
	l = [row[0] for row in fri]
	return l

def fetch_post(uid):
	flist = fetch_friend(uid)
	l = []
	for fri in flist:
		posts = db.execute("select uid, msg from Post where uid = ?", (fri,))
		for post in posts:
			d = {}
			d['id'] = post[0]
			d['message'] = post[1]
			l.append(d)
	return l

#---------Modify table----------
def del_account(uid):
	db.execute("delete from User where uid = ?", (uid,))
	db.execute("delete from Invite where send_id = ? or recv_id = ?", [uid, uid])
	db.execute("delete from Post where uid = ?", (uid,))
	db.execute("delete from Friendship where uid = ? or fid = ?", [uid, uid])
	conn.commit()

def createaccount(uid, fid):
	db.execute("insert into User (uid, pwd, token) values(?, ?, ?)", [uid, fid, None])
	conn.commit()

def tokenupdate(uid, status):
	if(status == 'login'):
		token = newtoken()
		while validation_token(token):
			token = newtoken()
	elif(status == 'logout'):
		token = None
	db.execute("update User set token = ? where uid = ?", [token, uid])
	conn.commit()

def createinvite(uid, fid):
	db.execute("insert into Invite (send_id, recv_id) values(?, ?)", [uid, fid])
	conn.commit()

def deleteinvite(uid, fid):
	db.execute("delete from Invite where send_id = ? and recv_id = ?", [fid, uid])
	conn.commit()

def createfriendship(uid, fid):
	db.execute("insert into Friendship (uid, fid) values (?, ?)", [uid, fid])
	db.execute("insert into Friendship (uid, fid) values (?, ?)", [fid, uid])
	conn.commit()

def addpost(uid, msg):
	db.execute("insert into Post (uid, msg) values(?, ?)", [uid, msg])
	conn.commit()

#message
def msg_parse(frag):
	l = [frag[i] for i in range(len(frag)) if i > 1]
	return ' '.join(l)
#-------------------------------------------------------------------------------------------------------------------------

#Creat a socket
HOST = sys.argv[1]
PORT = int(sys.argv[2])
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)


while True:
	(client, cliaddr) = server.accept()
	cmd = client.recv(4096).decode('utf-8')
	frag = cmd.split()

	response = {}
	if(cmd == 'exit'):
		client.close()
		continue

	if(frag[0] == 'register'):
		if(len(frag) == 3):
			if(existence(frag[1])):
				response['status'] = 1
				response['message'] = frag[1] + " is already used"
			else:
				createaccount(frag[1], frag[2])
				response['status'] = 0
				response['message'] = "Success!"
		else:
			response['status'] = 1
			response['message'] = "Usage: register <id> <password>"

	elif(frag[0] == 'login'):
		if(len(frag) == 3):
			if(validation_account(frag[1], frag[2])):
				tokenupdate(frag[1], frag[0])
				response['status'] = 0
				response['token'] = fetch_token(frag[1])
				response['message'] = "Success!"
			else:
				response['status'] = 1
				response['message'] =  "No such user or password error"
		else:
			response['status'] = 1
			response['message'] = "Usage: login <id> <password>"

	elif(frag[0] == 'delete'):
		print(len(frag))
		if(len(frag) == 2):
			if(validation_token(frag[1])):
				response['status'] = 0
				response['message'] = "Success!"
				del_account(fetch_uid(frag[1]))
			else:
				response['status'] = 1
				response['message'] = "Not login yet"
		elif(len(frag) == 1):
			response['status'] = 1
			response['message'] = "Not login yet"
		else:
			response['status'] = 1
			response['message'] = "Usage: delete <user>"

	elif(frag[0] == 'logout'):
		if(len(frag) == 2):
			if(validation_token(frag[1])):
				response['status'] = 0
				response['message'] = "Bye!"
				tokenupdate(fetch_uid(frag[1]), frag[0])
			else:
				response['status'] = 1
				response['message'] = "Not login yet"
		elif(len(frag) == 1):
			response['status'] = 1
			response['message'] = "Not login yet"
		else:
			response['status'] = 1
			response['message'] = "Usage: logout​ <user>"

	elif(frag[0] == 'invite'):
		if(len(frag) == 3):
			if(validation_token(frag[1])):
				uid = fetch_uid(frag[1])
				fid = frag[2]
				#already is your friend
				if(check_fship(uid, fid)):
					response['status'] = 1
					response['message'] = fid + " is already your friend"
				#fid doesn't exist
				elif(not existence(fid)):
					response['status'] = 1
					response['message'] = fid + " ​does not exist"
				#fid is uid
				elif(uid == fid):
					response['status'] = 1
					response['message'] = "You cannot invite yourself"
				#invited
				elif(check_invite(uid, fid)):
					response['status'] = 1
					response['message']  = "Already invited"
				#have been invited
				elif(check_invite(fid, uid)):
					response['status'] = 1
					response['message'] = fid + " has invited you"
				else:
					response['status'] = 0
					response['message'] = "Success!"
					createinvite(uid, fid)
			else:
				response['status'] = 1
				response['message'] = "Not login yet"
		elif(len(frag) == 1):
			response['status'] = 1
			response['message'] = "Not login yet"
		else:
			response['status'] = 1
			response['message'] = "Usage: invite​ <user> ​​<id>"

	elif(frag[0] == 'list-invite'):
		if(len(frag) == 2):
			if(validation_token(frag[1])):
				uid = fetch_uid(frag[1])
				response['status'] = 0
				response['invite'] = fetch_invited(uid)
			else:
				response['status'] = 1
				response['message'] = "Not login yet"
		elif(len(frag) == 1):
			response['status'] = 1
			response['message'] = "Not login yet"
		else:
			response['status'] = 1
			response['message'] = "Usage: list-invite​ <user>"

	elif(frag[0] == 'accept-invite'):
		if(len(frag) == 3):
			if(validation_token(frag[1])):
				uid = fetch_uid(frag[1])
				fid = frag[2]
				if(check_invite(frag[2], uid)):
					response['status'] = 0
					response['message'] = "Success!"
					createfriendship(uid, fid)
					deleteinvite(uid, fid)
				else:
					response['status'] = 1
					response['message'] = fid + " did not invite you"
			else:
				response['status'] = 1
				response['message'] = "Not login yet"
		elif(len(frag) == 1):
			response['status'] = 1
			response['message'] = "Not login yet"
		else:
			response['status'] = 1
			response['message'] = "Usage: accept-invite​ <user> ​​<id>"

	elif(frag[0] == 'list-friend'):
		if(len(frag) == 2):
			if(validation_token(frag[1])):
				uid = fetch_uid(frag[1])
				response['status'] = 0
				response['friend'] = fetch_friend(uid)
			else:
				response['status'] = 1
				response['message'] = "Not login yet"
		elif(len(frag) == 1):
			response['status'] = 1
			response['message'] = "Not login yet"
		else:
			response['status'] = 1
			response['message'] = "Usage: list-friend​ <user>"

	elif(frag[0] == 'post'):
		if(len(frag) >= 3):
			if(validation_token(frag[1])):
				uid = fetch_uid(frag[1])
				response['status'] = 0
				response['message'] = "Success!"
				addpost(uid, msg_parse(frag))
			else:
				response['status'] = 1
				response['message'] = "Not login yet"
		elif(len(frag) == 1):
			response['status'] = 1
			response['message'] = "Not login yet"
		else:
			response['status'] = 1
			response['message'] = "Usage: post​ <user>​​ <message>"

	elif(frag[0] == 'receive-post'):
		if(len(frag) == 2):
			if(validation_token(frag[1])):
				uid = fetch_uid(frag[1])
				response['status'] = 0
				response['post'] = fetch_post(uid)
			else:
				response['status'] = 1
				response['message'] = "Not login yet"
		elif(len(frag) == 1):
			response['status'] = 1
			response['message'] = "Not login yet"
		else:
			response['status'] = 1
			response['message'] = "Usage: receive-post​ <user>"

	else:
		response['status'] = 1
		response['message'] = "Unknown command " + frag[0]
	
	try:
		print(response)
		response = json.dumps(response)
		client.send(response.encode('utf-8'))
	except:
		print("Send error in response")

	client.close()