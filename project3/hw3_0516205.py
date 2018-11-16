from peewee import *
import socket
import json
import uuid
import sys

mysql_db = MySQLDatabase(host='140.113.168.202', user='holy', database='np', password='cscadb', charset='utf8mb4')
mysql_db.connect()

class BaseModel(Model):
	class Meta:
		database = mysql_db

class User(BaseModel):
	uid = CharField(primary_key=True, max_length=100)
	password = TextField()
	token = TextField(null=True, default=None)

class Invite(BaseModel):
	uid_sender = CharField(max_length=100)
	uid_receiver = CharField(max_length=100)
	class Meta:
		primary_key = CompositeKey('uid_sender', 'uid_receiver')

class Friend(BaseModel):
	uid = CharField(max_length=100)
	uid_friend = CharField(max_length=100)
	class Meta:
		primary_key = CompositeKey('uid', 'uid_friend')

class Post(BaseModel):
	uid = CharField(max_length=100)
	sender = CharField(max_length=100)
	message = TextField()

# create table
User.create_table()
Invite.create_table()
Friend.create_table()
Post.create_table()

def validate_token(token):
	user = User.select().where(User.token == token).dicts()
	if(len(user) > 0):
		return True
	else:
		return False

def get_uid(token):
	user = User.select().where(User.token == token).dicts()
	return user[0]['uid']

def check_uid_exist(uid):
	user = User.select().where(User.uid == uid).dicts()
	if(len(user) > 0):
		return True
	else:
		return False

def validate_account(uid, password):
	user = User.select().where(User.uid == uid, User.password == password).dicts()
	if(len(user) > 0):
		return True
	else:
		return False

def check_friendship(uid, uid_friend):
	check_friendship = Friend.select().where(Friend.uid == uid, Friend.uid_friend == uid_friend).dicts()
	if(len(check_friendship) > 0):
		return True
	else:
		return False

def check_already_invite(uid_sender, uid_receiver):
	invited = Invite.select().where(Invite.uid_sender == uid_sender, Invite.uid_receiver == uid_receiver).dicts()
	if(len(invited) > 0):
		return True
	else:
		return False

def has_be_invited(uid_sender, uid_receiver):
	invited = Invite.select().where(Invite.uid_sender == uid_receiver, Invite.uid_receiver == uid_sender).dicts()
	if(len(invited) > 0):
		return True
	else:
		return False

def create_token():
	return str(uuid.uuid1())

def check_token_exist(uid):
	user = User.select().where(User.uid == uid).dicts()
	if(user[0]['token'] == None):
		return False
	return True

def get_token(uid):
	user = User.select().where(User.uid == uid).dicts()
	return user[0]['token']

def list_invite(uid):
	array = []
	invite = Invite.select().where(Invite.uid_sender==uid).dicts()
	for row in invite:
		array.append(row['uid_receiver'])
	return array

def list_friend(uid):
	array = []
	friend = Friend.select().where(Friend.uid==uid).dicts()
	for row in friend:
		array.append(row['uid_friend'])
	return array

def create_friendship(uid, uid_friend):
	Friend.create(uid=uid, uid_friend=uid_friend)
	Friend.create(uid=uid_friend, uid_friend=uid)
	return None

def parse_message(tokens):
	sequence = []
	for i in range(len(tokens)):
		if(i == 0 or i == 1):
			continue
		sequence.append(tokens[i])
	message = ' '.join(sequence)
	return message

def post_message(sender, message):
	for friend in list_friend(sender):
		Post.create(uid=friend, sender=sender, message=message)
	return None

def list_post(uid):
	array = []
	post = Post.select().where(Post.uid==uid).dicts()
	for i in range(len(post)):
		obj = {}
		obj['id'] = post[i]['sender']
		obj['message'] = post[i]['message']
		array.append(obj)
	return array

def delete_account(uid):
	User.delete().where(User.uid==uid).execute()
	Invite.delete().where(Invite.uid_sender==uid).execute()
	Invite.delete().where(Invite.uid_receiver==uid).execute()
	Post.delete().where(Post.uid==uid).execute()
	Post.delete().where(Post.sender==uid).execute()
	Friend.delete().where(Friend.uid==uid).execute()
	Friend.delete().where(Friend.uid_friend==uid).execute()
	return None

HOST = ''
PORT = 80

# Set host and port through command line arguments
if(len(sys.argv) == 3):
	HOST = sys.argv[1]
	PORT = int(sys.argv[2])
else:
	print("Usage: python3 <filename> <host> <port>")
	sys.exit(0)

# Create socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)
print("Listening on " + HOST + " " + str(PORT))

while True:
	response = {}
	(client, caddress) = server.accept()
	msg = client.recv(4096) # bytes
	if not msg:
		continue
	else:
		request = msg.decode('utf-8') # bytes to str
		tokens = request.split()

		if(request == 'exit'):
			# if receive exit command, client will not send this case
			client.close()
			continue

		if(len(tokens) == 0):
			# if receive empty string or only spaces, client will not send this case
			response = tokens
		elif(tokens[0] == 'register'):
			if(len(tokens) == 3):
				if(check_uid_exist(tokens[1])):
					response['status'] = 1
					response['message'] = tokens[1] + " is already used"
				else:
					# db insert user account
					User.create(uid=tokens[1], password=tokens[2], token=None) 
					response['status'] = 0
					response['message'] = "Success!"
			else:
				response['status'] = 1
				response['message'] = "Usage: register <id> <password>"
		elif(tokens[0] == 'login'):
			if(len(tokens) == 3):
				if(not validate_account(tokens[1], tokens[2])):
					response['status'] = 1
					response['message'] = "No such user or password error"
				else:
					response['status'] = 0
					response['message'] = "Success!"
					if(check_token_exist(tokens[1])):
						response['token'] = get_token(tokens[1])
					else:
						# create token store in db
						new_token = create_token()
						User.update(token=new_token).where(User.uid==tokens[1]).execute()
						response['token'] = new_token
			else:
				response['status'] = 1
				response['message'] = "Usage: login <id> <password>"
		elif(tokens[0] == 'delete'):
			if(len(tokens) == 1):
				response['status'] = 1
				response['message'] = "Not login yet"
			elif(not validate_token(tokens[1])):
				response['status'] = 1
				response['message'] = "Not login yet"
			else:
				if(len(tokens) == 2):
					uid = get_uid(tokens[1])
					# db delete user, invites, posts, friends
					delete_account(uid)
					response['status'] = 0
					response['message'] = "Success!"
				else:
					response['status'] = 1
					response['message'] = "Usage: delete <user>"
		elif(tokens[0] == 'logout'):
			if(len(tokens) == 1):
				response['status'] = 1
				response['message'] = "Not login yet"
			elif(not validate_token(tokens[1])):
				response['status'] = 1
				response['message'] = "Not login yet"
			else:
				if(len(tokens) == 2):
					# db clear token
					User.update(token=None).where(User.token==tokens[1]).execute()
					response['status'] = 0
					response['message'] = "Bye!"
				else:
					response['status'] = 1
					response['message'] = "Usage: logout <user>"
		elif(tokens[0] == 'invite'):
			if(len(tokens) == 1):
				response['status'] = 1
				response['message'] = "Not login yet"
			elif(not validate_token(tokens[1])):
				response['status'] = 1
				response['message'] = "Not login yet"
			else:
				if(len(tokens) == 3):
					uid_sender = get_uid(tokens[1])
					uid_receiver = tokens[2]
					if(check_uid_exist(uid_receiver)):
						# uid is yourself
						if(uid_receiver == uid_sender):
							response['status'] = 1
							response['message'] = "You cannot invite yourself"
						# uid is your friend
						elif(check_friendship(uid_sender, uid_receiver)):
							response['status'] = 1
							response['message'] = tokens[2] + " is already your friend"
						# uid already be invited
						elif(check_already_invite(uid_sender, uid_receiver)):
							response['status'] = 1
							response['message'] = "Already invited"
						# uid has invited you
						elif(has_be_invited(uid_sender, uid_receiver)):
							response['status'] = 1
							response['message'] = tokens[2] + " has invited you"
						else:
							# db create invite
							Invite.create(uid_sender=uid_sender, uid_receiver=uid_receiver)
							response['status'] = 0
							response['message'] = "Success!"
					else:
						response['status'] = 1
						response['message'] =  tokens[2] + " does not exist"
				else:
					response['status'] = 1
					response['message'] = "Usage: invite <user> <id>"
		elif(tokens[0] == 'list-invite'):
			if(len(tokens) == 1):
				response['status'] = 1
				response['message'] = "Not login yet"
			elif(not validate_token(tokens[1])):
				response['status'] = 1
				response['message'] = "Not login yet"
			else:
				if(len(tokens) == 2):
					uid = get_uid(tokens[1])
					# db query return list
					response['invite'] = list_invite(uid)
					response['status'] = 0
					response['message'] = "Success!"
				else:
					response['status'] = 1
					response['message'] = "Usage: list-invite <user>"
		elif(tokens[0] == 'accept-invite'):
			if(len(tokens) == 1):
				response['status'] = 1
				response['message'] = "Not login yet"
			elif(not validate_token(tokens[1])):
				response['status'] = 1
				response['message'] = "Not login yet"
			else:
				if(len(tokens) == 3):
					uid_sender = tokens[2]
					uid_receiver = get_uid(tokens[1])
					# did not invite you 
					if(not check_already_invite(uid_sender, uid_receiver)):
						response['status'] = 1
						response['message'] = uid_sender + " did not invite you"
					else:
						# db delete invite, add friendship
						Invite.delete().where(Invite.uid_sender==uid_sender, Invite.uid_receiver==uid_receiver).execute()
						create_friendship(uid_sender, uid_receiver)
						response['status'] = 0
						response['message'] = "Success!"
				else:
					response['status'] = 1
					response['message'] = "Usage: accept-invite <user> <id>"
		elif(tokens[0] == 'list-friend'):
			if(len(tokens) == 1):
				response['status'] = 1
				response['message'] = "Not login yet"
			elif(not validate_token(tokens[1])):
				response['status'] = 1
				response['message'] = "Not login yet"
			else:
				if(len(tokens) == 2):
					uid = get_uid(tokens[1])
					# db query return list
					response['friend'] = list_friend(uid)
					response['status'] = 0
					response['message'] = "Success!"
				else:
					response['status'] = 1
					response['message'] = "Usage: list-friend <user>"
		elif(tokens[0] == 'post'):
			if(len(tokens) == 1):
				response['status'] = 1
				response['message'] = "Not login yet"
			elif(not validate_token(tokens[1])):
				response['status'] = 1
				response['message'] = "Not login yet"
			else:
				if(len(tokens) == 2):
					# "post user" command
					response['status'] = 1
					response['message'] = "Usage: post <user> <message>"
				else:
					sender = get_uid(tokens[1])
					# parse message, db add message to all friends inbox
					msg = parse_message(tokens)
					post_message(sender, msg)
					response['status'] = 0
					response['message'] = "Success!"
		elif(tokens[0] == 'receive-post'):
			if(len(tokens) == 1):
				response['status'] = 1
				response['message'] = "Not login yet"
			elif(not validate_token(tokens[1])):
				response['status'] = 1
				response['message'] = "Not login yet"
			else:
				if(len(tokens) == 2):
					uid = get_uid(tokens[1])
					# db query return list including user_id, message
					response['post'] = list_post(uid)
					response['status'] = 0
					response['message'] = "Success!"
				else:
					response['status'] = 1
					response['message'] = "Usage: receive-post <user>"
		# Unknown command
		else:
			response['message'] = "Unknown command " + tokens[0]
		
		# Send response to client
		try:
			print(response)
			response = json.dumps(response) # dict to string
			client.send(response.encode('utf-8')) # str to bytes
		except:
			print("Send response Error, response: " + response)
	
	client.close()