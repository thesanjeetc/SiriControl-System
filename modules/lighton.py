#You can import any required modules here
import requests


#This can be anything you want
moduleName = "lighton"

#All of the words must be heard in order for this module to be executed
commandWords = ["on", "lights"]

def execute(command):
    requests.get("https://sequematic.com/trigger-custom-webhook/........")
