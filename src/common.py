import subprocess
import sys
from datetime import datetime

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
    # print(data.args)
    # print(data.returncode)
    
    if data.returncode == 0:
        # print(data.stdout.decode())
        return {"status": True, "result" : data.stdout.decode()}
    else:
        # print(data.stderr.decode())
        return {"status": False, "result" : data.stderr.decode()}

    return data

def log(msg, status='INFO'):
    now = datetime.now()
    now = now.strftime('%d/%m/%Y %H:%M')

    with open('protheus-cli.log', 'a+',encoding='utf-8') as log_file:
        log_file.write(f'[{now}] [{status}] {msg}\n')

