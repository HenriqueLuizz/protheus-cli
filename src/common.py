import sys
import json
import subprocess
from datetime import datetime
from ipbot import bot_protheus

def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    
    if sys.platform not in platforms:
        return sys.platform
    
    return platforms[sys.platform]

    
def checkKey(d, k):
    if k in d:
        return True
    else:
        return False


def run(command:str):
    data = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    
    if data.returncode == 0:
        return {"status": True, "result" : data.stdout.decode()}
    else:
        return {"status": False, "result" : data.stderr.decode()}

    return data


def log(msg, status='INFO',send=False):
    now = datetime.now()
    now = now.strftime('%d/%m/%Y %H:%M')

    print(f'[{now}] [{status}] {msg}')

    with open('protheus-cli.log', 'a+',encoding='utf-8') as log_file:
        log_file.write(f'[{now}] [{status}] {msg}\n')

    if status != 'INFO':
        bot_protheus('Algo estranho está acontecendo lá no servidor. Olha isso!')
        bot_protheus(msg)

    if send:
        bot_protheus(msg)


def get_settings(key):
        with open('settings.json') as json_file:
            data = json.load(json_file)
            if key in data:
                return [True, data[key]]
            else:
                return [False]
