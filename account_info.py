USERNAME = ""
PASSWORD = ""

def setLogin(username, password):
    global USERNAME, PASSWORD
    USERNAME = username
    PASSWORD = password

def getLogin():
    return USERNAME, PASSWORD