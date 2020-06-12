import json
import subprocess
from common import log, run, get_settings
from ipbot import bot_protheus

class Oci:
    def __init__(self, ocid, startinstance, stopinstance, ip, enableservice, disableservice):
        self.ocid = ocid
        self.startinstance = startinstance
        self.stopinstance = stopinstance
        self.ip = ip
        self.enableservice = enableservice
        self.disableservice = disableservice
    
    def __repr__(self):
        return '<{}: {} - {} - {} - {} - {} - {}>\n'.format(self.__class__.__name__, self.ocid, self.startinstance, self.stopinstance, self.ip, self.enableservice, self.disableservice)

    def get_ocid(self):
        return self.ocid

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

    def set_ocid(self, ocid):
        self.ocid = ocid

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

    def get_config(self):
        
        list_oci = get_settings('oci')

        if list_oci[0]:
            return list_oci[1]
        else:
            return []
        
    def result_oci(self, d,send_msg=False, action='GET'):
        if d['status']:
            o = json.loads(d['result'])
            
            if 'data' in o:
                name = o['data']['display-name']
                lifecycle = o['data']['lifecycle-state']
                log(f'Instância {name} - {lifecycle}', 'INFO',True)
                
                if send_msg and action.lower() != 'get':
                    bot_protheus(f'Opa.. tudo bem!? \nAcabei de dar um ** {action.upper()} ** nas instâncias ** {name} ** da OCI. \n\nAgora ela está ** {lifecycle} **!!')

                return True
        else:
            log('Falha ao realizar a conexão com o OCI \n' + d['result'], 'ERROR')
            return False


    def check_oci(self, iids:list):
        for iid in iids:
            command=f'oci compute instance get --instance-id {iid}'
            data = run(command)
            if data['status']:
                self.result_oci(data)
                return True
            else:
                log(f'Falha ao realizar a conexão com o OCI \n' + data['result'], 'ERROR')
                return False
            break
        

    def instance_oci(self, iid: str, action='get'):
        
        log(f'OCI operation {action} running.','INFO')  
        
        if action.lower() == 'start':
            
            data = run(f'oci compute instance action --instance-id {iid} --action START')
            self.result_oci(data,True,action)
        elif action.lower() == 'stop':
            
            data = run(f'oci compute instance action --instance-id {iid} --action STOP')
            self.result_oci(data,True,action)
        else:
            data = run(f'oci compute instance get --instance-id {iid}')
            self.result_oci(data)
        
        log(f'OCI operation {action} finished.','INFO')
