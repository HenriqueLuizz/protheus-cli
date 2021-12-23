import json
from common import log
from ipoci import Oci
from ipaws import Aws

oci = object.__new__(Oci)
aws = object.__new__(Aws)


class Cloud:

    def __init__(self, **kwargs):
        self.instance = kwargs.get('instance', None)

    def identifyCloud(self):
        with open('settings.json') as json_file:
            data = json.load(json_file)
            for cloud in ['oci', 'aws', 'azure', 'gcp']:
                if cloud in data:
                    return [cloud]

    def get_oci(self, **kwargs):
        instance = -1

        if 'instance' in kwargs:
            instance = kwargs.get('instance')

        config = oci.get_config()
        return config if instance < 0 else config[instance]

    def change_state(self, **kwargs):

        clouds = self.identifyCloud()

        for c in clouds:
            if c == 'oci':
                self.oci(**kwargs)
            elif c == 'aws':
                self.aws(**kwargs)
            else:
                log(f'Sorry, {c.upper()} not yet supported!')
        return

    def aws(self, **kwargs):

        job = kwargs.get('job', None)
        ip = kwargs.get('ip')

        configs = aws.get_config()

        for inst_conf in configs:
            if ip in inst_conf['ip']:
                iid = inst_conf.get('iid', None)

                if iid is None:
                    # exception
                    log(f'AWS ID não configurado para o IP *{ip}*, por favor verificar as configurações no settings.json', 'ERROR')
                    return

                if job == 'stopinstance':
                    log(u'\U0001F5E3' + f'Iniciou o processo *{job.upper()}* do servidor *{ip}*', 'INFO', True)
                    aws.instance_aws(iid, 'STOP')
                    return
                elif job == 'startinstance':
                    log(u'\U0001F5E3' + f'Iniciou o processo *{job.upper()}* do servidor *{ip}*', 'INFO', True)
                    aws.instance_aws(iid, 'START')
                    return
                elif job == 'validate':
                    log(u'\U0001F5E3' + f'Iniciou o processo *{job.upper()}*', 'INFO', send=True)
                    aws.check_aws()
                    return
                else:
                    log(u'\U0001F5E3' + f'Iniciou o processo *{job.upper()}* do servidor *{ip}*', 'INFO')
                    aws.instance_aws(iid, 'GET')
                    return
        log('ID da instânce não encontrado!', 'WARN')
        return

    def oci(self, **kwargs):

        job = kwargs.get('job', None)
        ip = kwargs.get('ip')

        configs = oci.get_config()

        for inst_conf in configs:
            if ip in inst_conf['ip']:
                iid = inst_conf.get('ocid', None)
                region = inst_conf.get('region', None)

                if iid is None:
                    # exception
                    log(f'OCID não configurado para o IP *{ip}*, por favor verificar as configurações no settings.json', 'ERROR')
                    return

                if job == 'stopinstance':
                    log(u'\U0001F5E3' + f'Iniciou o processo *{job.upper()}* do servidor *{ip}*', 'INFO', True)
                    oci.instance_oci(iid, region, 'STOP')
                    return
                elif job == 'startinstance':
                    log(u'\U0001F5E3' + f'Iniciou o processo *{job.upper()}* do servidor *{ip}*', 'INFO', True)
                    oci.instance_oci(iid, region, 'START')
                    return
                else:
                    log(u'\U0001F5E3' + f'Iniciou o processo *{job.upper()}* do servidor *{ip}*', 'INFO')
                    oci.instance_oci(iid, region, 'GET')
                    return
        log('ID da instânce não encontrado!', 'WARN')
        return

    def set_oci(self, iids):
        conf = {}

        with open('settings.json') as json_file:
            conf = json.load(json_file)

            for iid in iids:
                log(f'OCID {iid} adicionado.')
                conf_add = {"ocid": iid, "ip": "", "name": "SERVER", "enableservice": "00:00", "disableservice": "00:00", "startinstance": "00:00", "stopinstance": "00:00", "repeat": "workingdays"}
                conf['oci'].append(conf_add)

        with open('settings.json', 'w') as json_read:
            json.dump(conf, json_read, indent=4)

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
            json.dump(conf, json_read, indent=4)

        return conf
