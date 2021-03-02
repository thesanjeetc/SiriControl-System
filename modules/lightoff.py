#You can import any required modules here
import requests

#This can be anything you want
moduleName = "lightoff"

#All of the words must be heard in order for this module to be executed
commandWords = ["off", "lights"]

def execute(command):
    requests.get("https://sequematic.com/trigger-custom-webhook/........")
