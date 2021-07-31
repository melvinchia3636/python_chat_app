import time

import socket
from _thread  import *

server = "192.168.1.198"
port = input("Please enter the port number: ")
password = input("Please enter the password you want: ")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, int(port)))
except :
    raise

s.listen()
print(f"Waiting for connection, server started at {server}:{port}")

message = []

def threaded_client(conn, addr):
    user = "anonymous"
    conn.send(str.encode(str(message), 'utf-8'))
    while True:
        try:
            data = conn.recv(9999999).decode()
            try: 
                data = eval(data)
                if data[-1] != password:
                    conn.sendall(str.encode(str(data), 'utf-8'))
                    break
                data = data[0]

                if 'CONSOLE' in data and user == "anonymous":
                    datalol = data.split(',')
                    user = datalol[1].replace(' JOINED THE CHAT', '')

                if not data:
                    data = [time.strftime("<%H:%M:%S", time.localtime())+'> '+'(CONSOLE)', user + ' LEFT THE CHAT']
                    with open('message.dat', 'a') as file:
                        file.write(str(data)+'\n')
                    conn.sendall(str.encode(str(data), 'utf-8'))
                    break
                elif data == " fetchHistories":
                    data = [i.replace('\n', '') for i in open('message.dat', 'r').readlines()]
                    data = data[-50:-1]
                elif data != ' ':
                    data = data.split(',')
                    with open('message.dat', 'a') as file:
                        file.write(str(data)+'\n')
                else:
                    data = [i.replace('\n', '') for i in open('message.dat', 'r').readlines()]
                    data = data[-1]
                conn.sendall(str.encode(str(data), 'utf-8'))
            except:
                raise
        except:
            data = [time.strftime("<%H:%M:%S", time.localtime())+'> '+'(CONSOLE)', user + ' LEFT THE CHAT']
            with open('message.dat', 'a') as file:
                    file.write(str(data)+'\n')
            break
        
    print('Lost connection')
    conn.close()


currentPlayer = 0
while True:
    conn, addr = s.accept()
    print('Connected to ', addr)
    start_new_thread(threaded_client, (conn, addr))
