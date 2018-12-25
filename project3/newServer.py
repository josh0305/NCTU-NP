import sqlite3
import socket 
import json
import uuid
import sys

class Server(object):
	def __init__(self, ip, port):
		try:
			self.db = sqlite3.connect('NP.db').cursor()
			if 0 < int(port) < 65535 :
				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
					s.bind((HOST, PORT))
					s.listen(5)
			else:
                raise Exception('Port value should between 1~65535')
        except Exception as e:
        	print(e, file=sys.stderr)
            sys.exit(1)

    def run(self):
    	while True:
    		(client, cliaddr) = server.accept()
    		cmd = client.recv(4096).decode()
    		resp = __judge_event(cmd)
    		print(resp)
    		resp = json.dumps()
    		try:
    			client.send(response.encode('utf-8'))
    			client.close()
    		except:
    			print('error in sending')

    def __judge_event(self, cmd = None):
    	if cmd:
    		frag = cmd.split()

    	

