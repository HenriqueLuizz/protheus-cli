import json
import click
from common import log
from ipoci import Oci
from ipbot import bot_protheus

oci = object.__new__(Oci)

class Cloud:

    def __init__(self,**kwargs):
        self.instance = kwargs.get('instance',None)


    def identifyCloud(self):
        with open('settings.json') as json_file:
            data = json.load(json_file)
            for cloud in ['oci','aws','azure','gcp']:
                if cloud in data:
                    return [cloud]

    def get_oci(self, **kwargs):
        instance = -1
        if 'instance' in kwargs: instance = kwargs.get('instance')
        config = oci.get_config()
        return config if instance < 0 else config[instance]
                   

    def change_state(self, **kwargs):
        
        clouds = self.identifyCloud()

        for c in clouds:
            if c == 'oci':
                self.oci(**kwargs)
            else:
                log(f'Sorry, {c.upper()} not yet supported!')
        
        return

    def oci(self,**kwargs):

        job = kwargs.get('job',None)
        ip = kwargs.get('ip')

        configs = oci.get_config()
        
        for inst_conf in configs:
            if ip in inst_conf['ip']:
                iid = inst_conf.get('ocid', None)
                
                if iid is None:
                    # exception
                    log(f'OCID não configurado para o IP {ip}, por favor verificar as configurações no settings.json','ERROR')
                    return

                if job == 'stopinstance':
                    log(f'Iniciou o processo {job.upper()} do servidor {ip}','INFO',True)
                    oci.instance_oci(iid,'STOP')
                    return
                elif job == 'startinstance':
                    log(f'Iniciou o processo {job.upper()} do servidor {ip}','INFO',True)
                    oci.instance_oci(iid,'START')
                    return
                else:
                    log(f'Iniciou o processo {job.upper()} do servidor {ip}','INFO')
                    oci.instance_oci(iid,'GET')
                    return
        log('ID da instânce não encontrado!','WARN')
        return


######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################


    def set_oci(self, iids):
        conf = {}

        with open('settings.json') as json_file:
            conf = json.load(json_file)
            
            for iid in iids:
                log(f'OCID {iid} adicionado.')
                conf['oci'].append(iid)

        with open('settings.json', 'w') as json_read:
            json.dump(conf, json_read,indent=4)

        return conf


    def remove_ocid(self, iids):
        conf = {}

        with open('settings.json') as json_file:
            conf = json.load(json_file)
            
            for iid in iids:
                if iid in conf['oci']:
                    while iid in conf['oci']:
                        log(f'OCID {iid} removido.')
                        conf['oci'].remove(iid)

        with open('settings.json', 'w') as json_read:
            json.dump(conf, json_read,indent=4)

        return conf

