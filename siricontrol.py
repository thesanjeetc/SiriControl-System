import time
import imaplib
import email
import os
import pkgutil

##########################################

#Add your gmail username and password here

username = ""
password = ""

##########################################

class Control():
    def __init__(self,username,password):
        print("------------------------------------------------------")
        print("-                    SIRI CONTROL                    -")
        print("-           Created by Sanjeet Chatterjee            -")
        print("-      Website: thereallycoolstuff.wordpress.com     -")
        print("------------------------------------------------------")
        try:
            self.username = username
            self.password = password
            self.last_checked = -1
            self.mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
            self.mail.login(username, password)
            self.mail.list()
            self.mail.select("Notes")
            try:
                #Gets last Note id to stop last command from executing
                result, uidlist = self.mail.search(None, "ALL")
                self.latest_email_id = uidlist[0].split()[-1]
                self.last_checked = self.latest_email_id
                self.load()
                self.handle()
            except IndexError:
                print("You have no Notes. Try creating one right now!")
                print("Then run this script again.")
        except imaplib.IMAP4.error:
            print("Your username and password is incorrect")
            print("Or IMAP is not enabled.")

    #Tries to loads all modules found in modules folder
    def load(self):
        print("\n")
        print("Loading modules...")
        self.modules = []
        path = os.path.join(os.path.dirname(__file__), "modules")
        directory = pkgutil.iter_modules(path=[path])
        for finder, name, ispkg in directory:
            try:
                 loader = finder.find_module(name)
                 module = loader.load_module(name)
                 if(hasattr(module,"commandWords") and hasattr(module,"moduleName") and hasattr(module,"execute")):
                     self.modules.append(module)
                     print("The module '" + name + "' has been loaded, successfully.")
                 else:
                     print("[ERROR] The module '" + name + "' is not in the correct format.")
            except:
                 print("[ERROR] The module '" + name + "' has some errors.")
        print("\n")

    #Retrieves the last Note created if new id found
    def fetch_command(self):
        self.mail.list()
        self.mail.select("Notes")
        result, uidlist = self.mail.search(None, "ALL")
        self.latest_email_id = uidlist[0].split()[-1]
        if self.latest_email_id == self.last_checked:
            return
        self.last_checked = self.latest_email_id
        result, data = self.mail.fetch(self.latest_email_id, "(RFC822)")
        voice_command = email.message_from_string(data[0][1].decode('utf-8'))
        c = str(voice_command.get_payload()).lower().strip()
        return c

    #Handles the command and execute module accordingly
    def handle(self):
        print("Fetching commands...")
        print("\n")
        while True:
            try:
                try:
                    self.command = self.fetch_command()
                    print("The word(s) '" + self.command + "' have been said")
                    foundWords = []
                    for module in self.modules:
                        for word in module.commandWords:
                            if(str(word) in self.command):
                                foundWords.append(str(word))
                        if(len(foundWords) == len(module.commandWords)):
                            try:
                                module.execute(self.command)
                                print("The module '" + str(module.moduleName) + "' has been executed successfully.")
                            except:
                                print("[ERROR] There has been an error when running the module '" + module.moduleName + "'.")
                        else:
                            print("\n")
                except TypeError:
                    pass
            except Exception as exc:
                print("Received an exception while running: {exc}"
                      "\nRestarting...".format(**locals()))
            time.sleep(1)

#Main logic   
if __name__ == '__main__':
    Control(username, password)
