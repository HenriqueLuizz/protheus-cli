# import subprocess
import json

from common import log, run, get_settings, set_settings


class Aws:
    def __init__(self, iid, name, startinstance, stopinstance, ip, enableservice, disableservice):
        self.iid = iid
        self.name = name
        self.startinstance = startinstance
        self.stopinstance = stopinstance
        self.ip = ip
        self.enableservice = enableservice
        self.disableservice = disableservice

    def __repr__(self):
        return '<{}: {} - {} - {} - {} - {} - {}>\n'.format(self.__class__.__name__, self.iid, self.startinstance, self.stopinstance, self.ip, self.enableservice, self.disableservice)

    def get_iid(self):
        return self.iid

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

    def set_iid(self, iid):
        self.iid = iid

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

            if 'InstanceStatuses' in o:
                name = o['InstanceStatuses'][0]['AvailabilityZone']
                lifecycle = o['InstanceStatuses'][0]['InstanceState']['Name']
                log(f'Instância *{name}* - *{lifecycle.upper()}*', 'INFO', send=send_msg)
                return True

            if 'Reservations' in o:
                name = o['Reservations'][0]['Instances'][0]['InstanceId']
                ip = o['Reservations'][0]['Instances'][0]['PrivateIpAddress']
                lifecycle = o['Reservations'][0]['Instances'][0]['State']['Name']
                log(f'Instância *{name}* (*{ip}*) - *{lifecycle.upper()}*', 'INFO', send=send_msg)
                return True

            if action.lower() != 'get':
                if 'StoppingInstances' in o:
                    name = o['StoppingInstances'][0]['InstanceId']
                    lifecycle = o['StoppingInstances'][0]['CurrentState']['Name']
                if 'StartingInstances' in o:
                    name = o['StartingInstances'][0]['InstanceId']
                    lifecycle = o['StartingInstances'][0]['CurrentState']['Name']
                log(u'\U0001F468\u200D\U0001F4BB'+ f' Acabei de dar um *{action.upper()}* nas instâncias *{name}* da AWS. \n\n' + u'\U0001F5A5' + f' Agora ela está *{lifecycle}* !!', 'INFO', send=send_msg)

            return True
        else:
            log(u'\U0001F525' + ' Falha ao realizar a conexão com o AWS \n' + d['result'], 'ERROR')
            return False

    def check_aws(self) -> bool:
        configs = self.get_config()

        for config in configs:
            command = f'aws ec2 describe-instances --instance-ids {config.get("iid")}'
            data = run(command)

            if data['status']:
                obj = json.loads(data['result'])
                ip = obj['Reservations'][0]['Instances'][0]['PrivateIpAddress']

                set_settings(key='aws', subkey='ip', value=ip, search=config.get("ip"))

                self.result_aws(d=data, send_msg=True)
            else:
                log('Falha ao realizar a conexão com o AWS \n' + data['result'], 'ERROR')

    def instance_aws(self, iid: str, action='get'):

        log(f'AWS operation *{action}* running.', 'INFO', send=True)

        if action.lower() == 'start':
            data = run(f'aws ec2 start-instances --instance-ids {iid}')
            self.result_aws(d=data, send_msg=True, action=action)
        elif action.lower() == 'stop':
            data = run(f'aws ec2 stop-instances --instance-ids {iid}')
            self.result_aws(d=data, send_msg=True, action=action)
        else:
            data = run(f'aws ec2 describe-instances --instance-ids {iid}')
            self.result_aws(d=data)

        log(f'AWS operation *{action}* finished.', 'INFO', send=True)
