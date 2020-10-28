import sys
import json
import subprocess
from datetime import datetime
from ipbot import bot_protheus


def get_platform():
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows'
    }

    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]


def checkKey(d, k):
    if k in d:
        return True
    else:
        return False


def run(command: str):
    data = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    if data.returncode == 0:
        return {"status": True, "result": data.stdout.decode()}
    else:
        return {"status": False, "result": data.stderr.decode()}


def log(msg, status='INFO', send=False, logfile='protheus-cli.log'):
    now = datetime.now()
    now = now.strftime('%d/%m/%Y %H:%M')

    print(f'[{now}] [{status}] {msg}')

    with open(logfile, 'a+', encoding='utf-8') as log_file:
        log_file.write(f'[{now}] [{status}] {msg}\n')

    if status != 'INFO':

        bot_protheus(u'\U0001F300' + 'Algo estranho está acontecendo lá no servidor. Olha isso!')
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


def set_settings(key, value, subkey='', search=''):
    configs = {}

    with open('settings.json') as json_file:
        configs = json.load(json_file)

        if key in configs:

            if type(configs[key]) == list:

                for idx, config in enumerate(configs[key]):

                    if subkey in config:

                        if search != '' and search == configs[key][idx][subkey]:
                            configs[key][idx][subkey] = value

                    else:
                        configs[key][idx] = value

            elif subkey != '' and subkey in configs[key]:
                configs[key][subkey] = value
            else:
                configs[key] = value

        with open('settings.json', 'w') as json_read:
            json.dump(configs, json_read, indent=4)

        return configs
