import sys
from network import Network
from tkinter import *
from tkinter import messagebox
from ttkbootstrap import Style
import tkinter.ttk as ttk
import time
import getpass
from plyer import notification 
import re

n = Network()

class MainWindow:
    def __init__(self):
        self.style = Style(theme="sandstone")
        self.root = self.style.master
        self.user = getpass.getuser()
        self.root.title('SMIRC - ' + self.user)
        self.root.attributes('-topmost', True)
        self.on_cooldown = False
    
        n.send(time.strftime("<%H:%M:%S", time.localtime())+'>'+' (CONSOLE)' + ',' + self.user + ' JOINED THE CHAT')

        try: self.prev_record = eval(n.send(" fetchHistories"))
        except: 
            messagebox.showerror('Error', "Something went wrong! Please check your password and try again. If you think this is a password, please contact the developer as soon as possible")
            sys.exit(5487)

        self.setup_widget()
        self.fetch_last()
        self.run()

    def change_theme(self, themename):
        try:
            self.style = Style(theme=themename)
            self.root.style = self.style
            self.style.root = self.root
            self.root.update()
        except: pass

    def fetch_last(self):
        for lol in self.prev_record:
            hmm = eval(lol)
            try:
                self.message.insert(END, hmm[0]+' : '+ hmm[1])
                self.message.insert(END, '\n')
            except:
                print(hmm)
        self.message.see(END)

        self.root.bind('<Return>', self.send_message)
    
    def setup_widget(self):
        self.container = ttk.Frame(self.root)
        self.container.pack(padx=10, pady=10)        
        self.message = Text(self.container)
        self.message.pack()
        self.inputbox = ttk.Entry(self.container)
        self.inputbox.pack(side="left", expand=True, fill=BOTH, pady=(10, 0), padx=(0, 10), ipadx=3, ipady=3)
        self.sendbutton = ttk.Button(self.container, text='SEND', command=self.send_message)
        self.sendbutton.pack(side='right', ipadx=10, ipady=3, pady=(10, 0))

    def disablecooldown(self):
        self.on_cooldown = False

    def send_message(self, *args):
        content = self.inputbox.get().strip()
        if content:
            if content.startswith('/'):
                if content == "/clear":
                    self.message.config(state=NORMAL)
                    self.message.delete(0.0, END)
                    self.message.config(state=DISABLED)
                    self.inputbox.delete(0, END)
                if (themename := re.match(r'^/theme (\w+)$', content)):
                    if (theme := themename.groups(0)):
                        self.change_theme(theme[0])
                        self.inputbox.delete(0, END)
            else:
                if content and not self.on_cooldown:
                    self.lol = eval(n.send(time.strftime("<%H:%M:%S", time.localtime())+'> '+self.user+','+content))
                    self.inputbox.delete(0, END)
                    self.on_cooldown = True
                    self.root.after(1000, self.disablecooldown)

    def run(self):
        lol = ' '

        while True:
            temp = n.send(' ')

            if lol != eval(temp):
                if isinstance(lol, list) and len(lol) > 0: 
                    notification.notify(title='title', message='m', ticker='r')
                lol = eval(temp)
                self.message.config(state=NORMAL)
                self.message.insert(END, lol[0]+' : '+lol[1])
                self.message.insert(END, '\n')
                self.message.config(state=DISABLED)
                self.message.see(END)

            try:
                self.root.update_idletasks()
                self.root.update()
            except:
                sys.exit(9487)

if __name__ == '__main__':
    application = MainWindow()
    application.root.mainloop()

