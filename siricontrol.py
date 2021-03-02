import time
import imaplib
import email
import os
import pkgutil
import sys
import subprocess
import unidecode
import requests
from imap_tools import MailBox, AND
##########################################

# Add your gmail username and password here

username = ""
password = ""

##########################################


class ControlException(Exception):
    pass


class Control():
    def __init__(self, username, password):
        print("------------------------------------------------------")
        print("-                    SIRI CONTROL                    -")
        print("-           Created by Sanjeet Chatterjee            -")
        print("-           Adapted by Pydathon                      -")
        print("-      Website: https://medium.com/@thesanjeetc      -")
        print("------------------------------------------------------")

        try:
            self.last_checked = -1
            self.mail = MailBox('imap.gmail.com')
            self.mail.login(username, password, initial_folder='Notes')
            
            # Gets last Note id to stop last command from executing
            uidlist = [msg.uid for msg in self.mail.fetch(AND(all=True))]
            subjects = [msg.subject for msg in self.mail.fetch(AND(all=True))]
            try:
                self.last_checked = uidlist[-1].split()[-1]
            except IndexError:
                pass
            self.load()
            self.handle()
        except imaplib.IMAP4.error:
            print("Your username and password is incorrect")
            print("Or IMAP is not enabled.")

    def load(self):
        """Try to load all modules found in the modules folder"""
        print("\n")
        print("Loading modules...")
        self.modules = []
        path = os.path.join(os.path.dirname(__file__), "modules")
        directory = pkgutil.iter_modules(path=[path])
        for finder, name, ispkg in directory:
            try:
                loader = finder.find_module(name)
                module = loader.load_module(name)
                if hasattr(module, "commandWords") \
                        and hasattr(module, "moduleName") \
                        and hasattr(module, "execute"):
                    self.modules.append(module)
                    print("The module '{0}' has been loaded, "
                          "successfully.".format(name))
                else:
                    print("[ERROR] The module '{0}' is not in the "
                          "correct format.".format(name))
            except:
                print("[ERROR] The module '" + name + "' has some errors.")
        print("\n")

    def fetch_command(self):
        """Retrieve the last Note created if new id found"""
        uidlist = [msg.uid for msg in self.mail.fetch(AND(all=True))]
        subjects = [msg.subject for msg in self.mail.fetch(AND(all=True))]
        try:
            latest_email_id = uidlist[-1].split()[-1]
        except IndexError:
            return

        if latest_email_id == self.last_checked:
            return

        self.last_checked = latest_email_id
        data = subjects[-1]
        return data.lower().strip()

    def handle(self):
        """Handle new commands
        Poll continuously every second and check for new commands.
        """
        print("Fetching commands...")
        print("\n")

        while True:
            folder_status = self.mail.folder.status('Notes') 
            nb_messages = folder_status["MESSAGES"] # permet d'actualiser la mailbox
            try:
                command = self.fetch_command()
                if not command:
                    raise ControlException("No command found.")
                print("The word(s) '" + unidecode.unidecode(str(command).lower()) + "' have been said")
                for module in self.modules:
                    foundWords = []
                    for word in module.commandWords:
                        #print("command=",unidecode.unidecode(str(command).lower()))
                        #print("word=", unidecode.unidecode(str(word).lower()))
                        #print(unidecode.unidecode(str(word).lower()) in unidecode.unidecode(str(command).lower()))
                        if unidecode.unidecode(str(word).lower()) in unidecode.unidecode(str(command).lower()):
                            foundWords.append(unidecode.unidecode(str(word).lower()))
                    if len(foundWords) == len(module.commandWords):
                        try:
                            module.execute(unidecode.unidecode(str(command).lower()))
                            print("The module {0} has been executed "
                                  "successfully.".format(module.moduleName))
                        except:
                            print("[ERROR] There has been an error "
                                  "when running the {0} module".format(
                                      module.moduleName))
                    else:
                        print("\n")
                    self.mail.move(self.mail.fetch(), 'notes_old')
            except (TypeError, ControlException):
                pass
            except Exception as exc:
                print("Received an exception while running: {exc}".format(
                    **locals()))
                print("Restarting...")
            time.sleep(1)


if __name__ == '__main__':
    Control(username, password)
