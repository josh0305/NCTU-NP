import socket
import json
import sys

user_token = {}

def replace(userid):
	s = cmd_token
	if(userid in user_token):
		s[1] = user_token[userid]
	str = ' '.join(s)
	return str

def delete_token(userid):
	if(userid in user_token):
		del user_token[userid]

def cli_send_rec(cli, text):
	cli.send(text.encode('utf-8'))
	out = json.loads(cli.recv(4096).decode('utf-8'))
	return out

host = sys.argv[1]
port = sys.argv[2]

while(1):
	cmd = input('')
	if cmd == 'exit':
		user_token.clear()
		break

	cmd_token = cmd.split()

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect((host, port))


	if(cmd_token[0] == 'register'):
		res = cli_send_rec(client, cmd)
		print(res['message'])

	elif(cmd_token[0] == 'login'):
		res = cli_send_rec(client, cmd)
		if(res['status'] == 0):
			user_token[cmd_token[1]] = res['token']
		print(res['message'])

	elif(cmd_token[0] == 'delete'):
		cmd = replace(cmd_token[1])
		res = cli_send_rec(client, cmd)
		if(res['status'] == 0):
			delete_token(cmd_token[1])
		print(res['message'])

	elif(cmd_token[0] == 'logout'):
		cmd = replace(cmd_token[1])
		res = cli_send_rec(client, cmd)
		if(res['status'] == 0):
			delete_token(cmd_token[1])
		print(res['message'])

	elif(cmd_token[0] == 'invite'):
		cmd = replace(cmd_token[1])
		res = cli_send_rec(client, cmd)
		print(res['message'])

	elif(cmd_token[0] == 'list-invite'):
		cmd = replace(cmd_token[1])
		res = cli_send_rec(client, cmd)
		if(res['status'] == 0):
			if(len(res['invite']) == 0):
				print('No invitations')
			else:
				for i in res['invite']:
					print(i)
		else:
			print(res['message'])

	elif(cmd_token[0] == 'accept-invite'):
		cmd = replace(cmd_token[1])
		res = cli_send_rec(client, cmd)
		print(res['message'])

	elif(cmd_token[0] == 'list_friend'):
		cmd = replace(cmd_token[1])
		res = cli_send_rec(client, cmd)
		if(res['status'] == 0):
			if(len(res['friend']) == 0):
				print('No friends')
			else:
				for i in res['friend']:
					print(i)
		else:
			print(res['message'])

	elif(cmd_token[0] == 'post'):
		cmd = replace(cmd_token[1])
		res = cli_send_rec(client, cmd)
		print(res['message'])

	elif(cmd_token[0] == 'receive-post'):
		cmd = replace(cmd_token[1])
		res = cli_send_rec(client, cmd)
		if(res['status'] == 0):
			if(len(res['post']) == 0):
				print('No posts')
			else:
				for i in res['post']:
					print(i['id'] + ': ' + i['message'])
		else:
			print(res['message'])

	else:
		print('Have no this command')
