# import subprocess
import json

from common import log, run, get_settings
from ipbot import bot_protheus


class Aws:
    def __init__(self, id, name, startinstance, stopinstance, ip, enableservice, disableservice):
        self.id = id
        self.name = name
        self.startinstance = startinstance
        self.stopinstance = stopinstance
        self.ip = ip
        self.enableservice = enableservice
        self.disableservice = disableservice

    def __repr__(self):
        return '<{}: {} - {} - {} - {} - {} - {}>\n'.format(self.__class__.__name__, self.ocid, self.startinstance, self.stopinstance, self.ip, self.enableservice, self.disableservice)

    def get_id(self):
        return self.id

    def get_startinstance(self):
        return self.startinstance

    def get_stopinstance(self):
        return self.stopinstance

    def get_ip(self):
        return self.ip

    def get_enableservice(self):
        return self.enableservice

    def get_disableservice(self):
        return self.disableservice

    def set_id(self, id):
        self.id = id

    def set_startinstance(self, startinstance):
        self.startinstance = startinstance

    def set_stopinstance(self, stopinstance):
        self.stopinstance = stopinstance

    def set_ip(self, ip):
        self.ip = ip

    def set_enableservice(self, enableservice):
        self.enableservice = enableservice

    def set_disableservice(self, disableservice):
        self.disableservice = disableservice

    def get_config(self) -> list:
        list_aws = get_settings('aws')

        if list_aws[0]:
            return list_aws[1]
        else:
            return []

    def result_aws(self, d, send_msg=False, action='GET') -> bool:
        if d['status']:
            o = json.loads(d['result'])
            print(o)
            if 'InstanceStatuses' in o:
                name = o['InstanceStatuses'][0]['AvailabilityZone']
                lifecycle = o['InstanceStatuses'][0]['InstanceState']['Name']
                print(name)
                print(lifecycle)
                log(f'Instância {name} - {lifecycle.upper()}', 'INFO', True)

                if send_msg and action.lower() != 'get':
                    bot_protheus(f'Opa.. tudo bem!? \nAcabei de dar um ** {action.upper()} ** nas instâncias ** {name} ** da AWS. \n\nAgora ela está ** {lifecycle} **!!')

                return True
        else:
            log('Falha ao realizar a conexão com o AWS \n' + d['result'], 'ERROR')
            return False

    def check_aws(self, iids: list) -> bool:
        for iid in iids:
            command = f'aws compute instance get --instance-id {iid}'
            data = run(command)
            if data['status']:
                self.result_aws(data)
                return True
            else:
                log('Falha ao realizar a conexão com o AWS \n' + data['result'], 'ERROR')
                return False
            break

    def instance_aws(self, iid: str, action='get'):

        log(f'AWS operation {action} running.', 'INFO')

        if action.lower() == 'start':
            data = run(f'aws ec2 start-instances --instance-ids {iid}')
            self.result_aws(data, True, action)
        elif action.lower() == 'stop':
            data = run(f'aws ec2 stop-instances --instance-ids {iid}')
            self.result_aws(data, True, action)
        else:
            data = run(f'aws ec2 describe-instance-status --instance-id {iid}')
            
            self.result_aws(data)

        log(f'AWS operation {action} finished.', 'INFO')
