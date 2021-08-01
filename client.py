import sys
from network import Network
from tkinter import *
from tkinter.font import Font
from ttkbootstrap import Style
import tkinter.ttk as ttk
import time
import getpass
import re
import json
from constants import *

network = Network()

class MessageContainer(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit",
                                count=count, regexp=regexp)
            if index == "": break
            if count.get() == 0: break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_remove("usertag", "matchStart", "matchEnd")
            self.tag_add(tag, "matchStart", "matchEnd")

class MainWindow:

    def __init__(self):
        self.style = Style(theme="sandstone")
        self.root = self.style.master

        self.BOLD_FONT = Font(weight="bold", size=12, family="Consolas")
        self.NORMAL_FONT = Font(weight="normal", size=12, family="Consolas")

        self.user = getpass.getuser().lower().replace(' ', '')
        self.root.title('SMIRC - ' + self.user)
        self.root.attributes('-topmost', True)
        self.on_cooldown = False
        self.typed_message = []
        self.typed_message_cursor = 0
    
        self.id = network.send({
            "type": "chat_join",
            "content": {
                "user": self.user,
                "time": time.strftime("%H:%M:%S", time.localtime()),
            }
        })

        self.get_chat_record()
        self.setup_widget()
        self.place_widget()
        self.bind_events()
        self.tags_configure()
        self.load_chat_record()
        self.run()

    def get_chat_record(self):
        prev_record = network.send({
            "type": "fetch_histories"
        })
        if prev_record.strip():
            try: self.prev_record = json.loads(prev_record)
            except: self.get_chat_record()
        else: self.get_chat_record()

    def load_chat_record(self):
        for hmm in self.prev_record:
            try:
                self.message.insert(END, hmm[0])
                self.message.insert(END, ' : '+hmm[1])
                self.message.insert(END, '\n')
            except:
                pass

        self.message.see(END)
    
    def setup_widget(self):
        self.container = ttk.Frame(self.root)
        self.message = MessageContainer(self.container, bg=self.style.colors.get('bg'), font=self.NORMAL_FONT)
        self.inputbox = ttk.Entry(self.container, font=self.NORMAL_FONT)
        self.sendbutton = ttk.Button(self.container, text='SEND', command=self.send_message)

        self.style_configure()

    def place_widget(self):
        self.container.pack(padx=10, pady=10, expand=True, fill=BOTH)
        self.message.pack(expand=True, fill=BOTH)
        self.inputbox.pack(side="left", expand=True, fill=BOTH, pady=(10, 0), padx=(0, 10), ipadx=3, ipady=3)
        self.sendbutton.pack(side='right', ipadx=10, ipady=3, pady=(10, 0))
        
    def style_configure(self):
        self.style.configure('TEntry', insertcolor=self.style.colors.get('primary'))
        self.style.configure('TButton', font=self.BOLD_FONT)
        self.root.update()

    def tags_configure(self):
        tags = [
            ['meta', self.BOLD_FONT, self.style.colors.get('primary'), self.style.colors.get('bg')],
            ['usertag', self.BOLD_FONT, self.style.colors.get('bg'), self.style.colors.get('inputfg')],
            ['userleft', self.BOLD_FONT, self.style.colors.get('danger'), self.style.colors.get("bg")],
            ['userjoined', self.BOLD_FONT, self.style.colors.get('success'), self.style.colors.get("bg")],
            ['consoleoutput', None, self.style.colors.get("info"), None]
        ]

        for tagname, font, fg, bg in tags:
            self.message.tag_configure(tagname, font=font, foreground=fg, background=bg)

        self.style_configure()

    def bind_events(self):
        self.inputbox.bind('<Return>', self.send_message)
        self.inputbox.bind('<Up>', self.show_last_message)
        self.inputbox.bind('<Down>', self.show_next_message)

    def show_last_message(self, *_):
        self.typed_message_cursor -= 1
        try: content = self.typed_message[self.typed_message_cursor]
        except: 
            content = ""
            self.typed_message_cursor = 0
        self.inputbox.delete(0, END)
        self.inputbox.insert(0, content)

    def show_next_message(self, *_):
        if self.typed_message_cursor+1 <= 0:
            if self.typed_message_cursor == -1:
                self.inputbox.delete(0, END)
                self.typed_message_cursor = 0
            else:
                self.typed_message_cursor += 1
                content = self.typed_message[self.typed_message_cursor]
                self.inputbox.delete(0, END)
                self.inputbox.insert(0, content)

    def disable_cooldown(self):
        self.on_cooldown = False

    def send_message(self, *_):
        content = self.inputbox.get().strip()
        if content:
            if content.startswith('/'):
                self.handle_command(content)
            else:
                if content and not self.on_cooldown:
                    network.send({
                        "type": "chat_send",
                        "content": {
                            "user": self.user,
                            "user_id": self.id,
                            "time": time.strftime("%H:%M:%S", time.localtime()),
                            "content": content[:200]
                        }
                        })
                    self.inputbox.delete(0, END)
                    self.on_cooldown = True
                    self.root.after(1000, self.disable_cooldown)
            
            if not self.typed_message or content != self.typed_message[-1]:
                self.typed_message.append(content)
            self.typed_message_cursor = 0

    def handle_command(self, content):
        if content == "/clear":
            self.message.config(state=NORMAL)
            self.message.delete(0.0, END)
            self.message.config(state=DISABLED)
            self.inputbox.delete(0, END)

        if (themename := re.match(r'^/theme (\w+)$', content)):
            if (theme := themename.groups(0)):
                if theme[0] == "help":
                    self.message.config(state=NORMAL)
                    self.message.insert(END, time.strftime("[%H:%M:%S] <CONSOLE> : ", time.localtime()), 'meta')
                    self.message.insert(END, str(self.style._theme_names), "consoleoutput")
                    self.message.config(state=DISABLED)
                    self.message.see(END)
                    self.inputbox.delete(0, END)
                else:
                    self.change_theme(theme[0])
                    self.inputbox.delete(0, END)

        if (opacity := re.match(r'^/opacity ([\d|.]+)$', content)):
            if (value := opacity.groups(0)):
                self.change_opacity(float(value[0]))
                self.inputbox.delete(0, END)

        if (fontsize := re.match(r'^/fontsize (\d+)$', content)):
            if (value := fontsize.groups(0)):
                self.change_fontsize(int(value[0]))
                self.inputbox.delete(0, END)

        if (fontfamily := re.match(r'^/fontfamily (.+)$', content)):
            if (value := fontfamily.groups(0)):
                self.change_fontfamily(value[0])
                self.inputbox.delete(0, END)

        if content == "/help":
                self.message.config(state=NORMAL)
                self.message.insert(END, time.strftime("[%H:%M:%S] <CONSOLE> :", time.localtime()), 'meta')
                self.message.insert(END, """
/help \t\t\t\t- List out all the commands available
/theme <name> \t\t\t\t- change the theme color of the chat window
/opacity <value 0.0 - 1.0> \t\t\t\t- change the opacity of the chat window
/clear \t\t\t\t- clear the chat message

""", "consoleoutput")
                self.message.config(state=DISABLED)
                self.message.see(END)
                self.inputbox.delete(0, END)

    def change_theme(self, themename):
        try:
            self.style = Style(theme=themename)
            self.root.style = self.style
            self.style.root = self.root
            self.root.config(bg=self.style.colors.get('bg'))
            self.tags_configure()
            self.message.config(background=self.style.colors.get('bg'), foreground=self.style.colors.get('fg'), highlightbackground=self.style.colors.get('border'))
            self.root.update()
        except: pass

    def change_opacity(self, value):
        self.root.attributes('-alpha', value)

    def change_fontsize(self, value):
        self.BOLD_FONT['size'] = value
        self.NORMAL_FONT['size'] = value

        self.root.update()
        self.message.see(END)
        self.inputbox.delete(0, END)

    def change_fontfamily(self, value):
        self.BOLD_FONT['family'] = value
        self.NORMAL_FONT['family'] = value

        self.root.update()
        self.message.see(END)
        self.inputbox.delete(0, END)

    def run(self):
        message = ' '

        while True:
            temp = network.send({
                "type": "chat_fetch"
            })

            if message != json.loads(temp):
                message = json.loads(temp)
                self.message.config(state=NORMAL)
                self.message.insert(END, message[0])
                self.message.insert(END, ' : '+message[1])
                self.message.insert(END, '\n')
                self.message.highlight_pattern(r".+CONSOLE.+LEFT.+", "userleft", regexp=True)
                self.message.highlight_pattern(r".+CONSOLE.+JOINED.+", "userjoined", regexp=True)
                self.message.highlight_pattern(r"#\d+", "usertag", regexp=True)
                self.message.highlight_pattern(r"\[.*?\] <.*?> :", "meta", regexp=True)
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