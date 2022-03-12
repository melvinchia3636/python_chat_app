import socket
import sys
import requests
import re
from tkinter import *
import tkinter.ttk as ttk
from ttkbootstrap import Style
import requests
import os

if not os.path.exists('recent.dat'): open('recent.dat', 'w')

style = Style(theme="sandstone")
win = style.master
win.title('SMIRC')
win.protocol("WM_DELETE_WINDOW", lambda: sys.exit(9487))

my_ip, port, password = '', None, ''
ip = requests.get('http://ip.42.pl/raw').text

def connect():
    global my_ip, port, password
    my_ip, port, password = my_ip_entry.get(), int(port_entry.get()), password_entry.get().strip()
    if my_ip not in open('recent.dat', 'r').read():
        open('recent.dat', 'a').write(my_ip+'\n')
    win.destroy()

container = Frame(win)
my_ip_label = Label(container, text="IP Address:", justify="left")
port_label = Label(container, text="Port Number:", justify="left")
password_label = Label(container, text="Password:", justify="left")
my_ip_entry = ttk.Combobox(container, values=[i.strip() for i in open('recent.dat', 'r').readlines()][::-1])
port_entry = ttk.Entry(container)
password_entry = ttk.Entry(container)
connect_btn = ttk.Button(container, text="CONNECT", command=connect)
win.bind('<Return>', lambda e: connect())

container.pack(padx=10, pady=10)
my_ip_label.grid(row=0, column=0, sticky='W', pady=3, padx=(0, 10))
port_label.grid(row=1, column=0, sticky='W', pady=3, padx=(0, 10))
my_ip_entry.grid(row=0, column=1, pady=3)
port_entry.grid(row=1, column=1, pady=3, ipadx=7)
password_label.grid(row=2, column=0, sticky='W', pady=3, padx=(0, 10))
password_entry.grid(row=2, column=1, pady=3, ipadx=7)
connect_btn.grid(row=3, column=0, columnspan=2, pady=(10, 0))

win.mainloop()

class Network:
    global port
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = my_ip
        self.port = port
        self.addr = (self.server, self.port)
        self.pos = self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(8192).decode('utf-8')
        except:
            sys.exit(0)

    def send(self, data):
        try:
            self.client.send(str.encode(str([data, password]), 'utf-8'))
            return self.client.recv(8192).decode('utf-8')
        except socket.error as e:
            print(e)