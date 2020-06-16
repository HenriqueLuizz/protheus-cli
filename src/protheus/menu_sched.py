# import time
import json
import schedule

from menu_service import Service
from common import log
# from menu_cloud import Cloud
# from ipbot import bot_protheus


class Scheduler:

    def __init__(self, enableservice, disableservice, startinstance, stopinstance, repeat):
        self.enableservice = enableservice
        self.disableservice = disableservice
        self.startinstance = startinstance
        self.stopinstance = stopinstance
        self.repeat = repeat

    def weekdays(self, repeat=None) -> list:
        if repeat == 'workingdays' or repeat == 'working-days' or repeat == 'diasuteis' or repeat == 'dias-uteis':
            return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        elif repeat in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            return repeat
        elif repeat == 'daily' or repeat == 'diariamente':
            return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        else:
            log('Configuração da chave inválida, valores válido <workingdays|daily|monday..sunday> ', 'ERROR')
            return []

    def get_enableservice(self):
        return self.enableservice

    def get_disableservice(self):
        return self.disableservice

    def get_startinstance(self):
        return self.startinstance

    def get_stopinstance(self):
        return self.stopinstance

    def get_repeat(self):
        return self.repeat

    def set_enableservice(self, enableservice):
        self.enableservice = enableservice

    def set_disableservice(self, disableservice):
        self.disableservice = disableservice

    def set_startinstance(self, startinstance):
        self.startinstance = startinstance

    def set_stopinstance(self, stopinstance):
        self.stopinstance = stopinstance

    def set_repeat(self, repeat):
        self.repeat = repeat

    def get_config(self) -> dict:
        conf: dict = {}
        with open('settings.json') as json_file:
            conf = json.load(json_file)
        return conf

    def set_config(self, key, value) -> dict:
        conf: dict = {}

        with open('settings.json') as json_file:
            conf = json.load(json_file)
            conf.update(dict({key: value}))

        with open('settings.json', 'w') as json_read:
            json.dump(conf, json_read, indent=4)

        log(f'Arquivo de configuração alterado | chave: {key} , valor: {value}')
        return conf

    def load(self):
        data = self.get_config()
        self.enableservice = data.get('enableservice', '')
        self.disableservice = data.get('disableservice', '')
        self.startinstance = data.get('startinstance', '')
        self.stopinstance = data.get('stopinstance', '')
        self.repeat = data.get('repeat', '')

    def set_schedule(self, serv: Service, **kwargs):

        global_time: bool = False

        kw_ip: str = kwargs.get('ip', None)
        kw_name: str = kwargs.get('name', None)
        # enableservice, disableservice, startinstance, stopinstance
        kw_job: str = kwargs.get('job', None)
        kw_jobtime: str = kwargs.get('jobtime', None)
        kw_repeat: str = kwargs.get('repeat', None)

        if kw_jobtime is None:
            global_time = True

        # Compara o valor da variavel referente ao Job solicitado com o valor da variavel jobtime passada, retorna o valor da variavel jobtime se ela não for None, caso contrario retorna o valor da variavel do job geral
        hour = self.valid_hour(getattr(self, kw_job), kw_jobtime)
        repeat = self.valid_repeat(self.get_repeat(), kw_repeat)
        list_repeat = self.weekdays(repeat)

        log(f'Agendamento de {kw_job.upper()} para o {kw_name.upper()} ({kw_ip}) às {hour} | {repeat} ', 'INFO', True)

        if len(list_repeat) > 0:
            for day in list_repeat:
                getattr(schedule.every(), day).at(hour).do(serv.case_job, global_time=global_time, **kwargs)

    def valid_hour(self, hour_sched: str, hour: str) -> str:
        if hour is None:
            return hour_sched
        return hour

    def valid_repeat(self, repeat_sched: str, repeat: str) -> str:
        if repeat is None:
            return repeat_sched
        return repeat
