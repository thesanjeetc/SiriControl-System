import time
import imaplib
import email
import os
import pkgutil
from os.path import expanduser, dirname, exists, join, abspath
from base64 import b64encode, b64decode 

##########################################

# Add your gmail username and password to 
# a file called .siricontrolsecret

##########################################

SECFILE = ".siricontrolsecret"
def get_credentials():
    possible_locations = set([
        expanduser('~'), 
        abspath(dirname(__file__)),
        os.getcwd()
    ])
    user = ""
    pwd = ""
    for dir_path in possible_locations:
        sec_path = join(dir_path, SECFILE) 
        if exists(sec_path):
            try:
                sf = open(sec_path, "r")
                lines = sf.readlines()
                user = lines[0].strip()
                pwd = lines[1].strip()
                sf.close()
                if not pwd.startswith("{enc}"):
                    # pwd not encoded
                    pwd = "{enc}" + b64encode(pwd)
                    sf = open(sec_path, "w")
                    sf.write("\n".join([user , pwd]))
                    sf.close()
                return user, b64decode(pwd[5:])
            except IOError as e:
                print("Found " + sec_path + " but I couldn't read it: " + e)
            except IndexError:
                print("File " + sec_path + " must contain two lines, " + 
                " username and password, to be valid.")

    #still here? I couldn't find anything
    raise Exception(SECFILE + 
                    " not found, please create it" + 
                    " in one of these folders:\n" +
                    "\n".join(possible_locations))

class ControlException(Exception):
    pass


class Control():
    def __init__(self, username, password):
        print("------------------------------------------------------")
        print("-                    SIRI CONTROL                    -")
        print("-           Created by Sanjeet Chatterjee            -")
        print("-      Website: thereallycoolstuff.wordpress.com     -")
        print("------------------------------------------------------")

        try:
            self.last_checked = -1
            self.mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            self.mail.login(username, password)
            self.mail.list()
            self.mail.select("Notes")

            # Gets last Note id to stop last command from executing
            result, uidlist = self.mail.search(None, "ALL")
            try:
                self.last_checked = uidlist[0].split()[-1]
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
        self.mail.list()
        self.mail.select("Notes")

        result, uidlist = self.mail.search(None, "ALL")
        try:
            latest_email_id = uidlist[0].split()[-1]
        except IndexError:
            return

        if latest_email_id == self.last_checked:
            return

        self.last_checked = latest_email_id
        result, data = self.mail.fetch(latest_email_id, "(RFC822)")
        voice_command = email.message_from_string(data[0][1].decode('utf-8'))
        return str(voice_command.get_payload()).lower().strip()

    def handle(self):
        """Handle new commands

        Poll continuously every second and check for new commands.
        """
        print("Fetching commands...")
        print("\n")

        while True:
            try:
                command = self.fetch_command()
                if not command:
                    raise ControlException("No command found.")

                print("The word(s) '" + command + "' have been said")
                for module in self.modules:
                    foundWords = []
                    for word in module.commandWords:
                        if str(word) in command:
                            foundWords.append(str(word))
                    if len(foundWords) == len(module.commandWords):
                        try:
                            module.execute(command)
                            print("The module {0} has been executed "
                                  "successfully.".format(module.moduleName))
                        except:
                            print("[ERROR] There has been an error "
                                  "when running the {0} module".format(
                                      module.moduleName))
                    else:
                        print("\n")
            except (TypeError, ControlException):
                pass
            except Exception as exc:
                print("Received an exception while running: {exc}".format(
                    **locals()))
                print("Restarting...")
            time.sleep(1)


if __name__ == '__main__':
    Control(get_credentials())
