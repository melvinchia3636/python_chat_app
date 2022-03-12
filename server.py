import time

import socket
from _thread  import *
import random
import re
import json

server = "192.168.1.198"
port = input("Port number: ")
password = input("Password: ")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try: s.bind((server, int(port)))
except : raise

s.listen()
print(f"Waiting for connection, server started at {server}:{port}")

message = []
user = []

def write_data(data):
    content = json.load(open('message.json', 'r'))
    content.append(data)
    json.dump(content, open('message.json', 'w'))

def get_id():
    num = str(random.randint(1, 9999)).zfill(4)
    if num not in [i[1] for i in user]: return num
    return get_id()

def threaded_client(conn, addr):
    new_user = "anonymous"
    conn.send(str.encode(str(message), 'utf-8'))
    while True:
        try:
            data = conn.recv(8192).decode()
            try: data = eval(data)
            except: continue
            if data[-1] != password:
                conn.sendall(str.encode(str(data), 'utf-8'))
                break
            data = data[0]

            if data["type"] == "chat_join":
                data = data['content']
                new_user = data['user']
                new_user_id = get_id()
                data = ["[{}] <CONSOLE>".format(data['time']), "{}#{} JOINED THE CHAT".format(new_user, new_user_id)]
                user.append((new_user, new_user_id))
                
                write_data(data)
                conn.sendall(str.encode(new_user_id, 'utf-8'))
            
            elif data["type"] == "fetch_histories":
                data = json.load(open('message.json', 'r'))
                data = data[-60:-1]
                conn.sendall(str.encode(json.dumps({
                    "type": "histories",
                    "content": data
                }), 'utf-8'))
            
            elif data["type"] == "chat_send":
                data = data['content']
                data = ["[{}] <{}#{}>".format(data['time'], data['user'], data['user_id']), data['content']]
                write_data(data)
                if (match := re.findall(r'#(\d+)', data[1])):
                    for i in match:
                        print(i)
                conn.sendall(str.encode(str(data), 'utf-8'))
            
            elif data["type"] == "chat_fetch":
                data = json.load(open('message.json', 'r'))
                data = data[-1]
                if data: conn.sendall(str.encode(json.dumps({
                    "type": "chat_fetch",
                    "content": data
                }), 'utf-8'))
                else: conn.sendall(str.encode(str([]), 'utf-8'))
        except:
            raise
            if new_user != "anonymous":
                data = [time.strftime("[%H:%M:%S] <CONSOLE>", time.localtime()), f'{new_user}#{new_user_id} LEFT THE CHAT']
                user.remove((new_user, new_user_id))
                write_data(data)
                conn.sendall(str.encode(str(data), 'utf-8'))
            break
        
    print('{}<{}#{}> disconnected'.format(new_user.title(), *addr))
    conn.close()


currentPlayer = 0
while True:
    conn, addr = s.accept()
    print('Connected to {}#{}'.format(*addr))
    start_new_thread(threaded_client, (conn, addr))