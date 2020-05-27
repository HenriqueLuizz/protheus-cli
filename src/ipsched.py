import json
import time
import schedule
from ipservice import Service
from ipcloud import Cloud
from common import log, checkKey
from ipbot import bot_protheus

class Scheduler:

    def __init__(self, enableservice, disableservice, startinstance, stopinstance, repeat):
        self.enableservice = enableservice
        self.disableservice = disableservice
        self.startinstance = startinstance
        self.stopinstance = stopinstance
        self.repeat = repeat
    

    def weekdays(self, repeat=None):
        if repeat == 'workingdays' or repeat == 'working-days' or repeat == 'diasuteis' or repeat == 'dias-uteis':
            return ['monday','tuesday','wednesday','thursday','friday']
        elif repeat in ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']:
            return repeat
        elif repeat == 'daily' or repeat == 'diariamente':
            return ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        else:
            log('Configuração da chave inválida, valores válido <workingdays|daily|monday..sunday> ','ERROR')
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

    
    def get_config(self):
        conf = {}
        with open('settings.json') as json_file:
            conf = json.load(json_file)
        return conf


    def set_config(self, key, value):
        conf = {}

        with open('settings.json') as json_file:
            conf = json.load(json_file)
            conf.update(dict({key:value}))

        with open('settings.json', 'w') as json_read:
            json.dump(conf, json_read,indent=4)

        log(f'Arquivo de configuração alterado | chave: {key} , valor: {value}')
        return conf


    def load(self):
        data = self.get_config()
        self.enableservice = data.get('enableservice','')
        self.disableservice = data.get('disableservice','')
        self.startinstance = data.get('startinstance','')
        self.stopinstance = data.get('stopinstance','')
        self.repeat = data.get('repeat','')

    
    def set_schedule(self, serv:Service, **kwargs):

        global_time = False

        kw_ip = kwargs.get('ip',None)
        kw_name = kwargs.get('name',None)
        kw_job = kwargs.get('job',None) # enableservice, disableservice, startinstance, stopinstance
        kw_jobtime = kwargs.get('jobtime',None)
        kw_repeat = kwargs.get('repeat',None)

        if kw_jobtime is None:
            global_time = True

        hour = self.valid_hour(getattr(self,kw_job),kw_jobtime) # Compara o valor da variavel referente ao Job solicitado com o valor da variavel jobtime passada, retorna o valor da variavel jobtime se ela não for None, caso contrario retorna o valor da variavel do job geral
        repeat = self.valid_repeat(self.get_repeat(),kw_repeat)
        list_repeat = self.weekdays(repeat)

        log(f'Agendamento de {kw_job.upper()} para o {kw_name.upper()} ({kw_ip}) às {hour} | {repeat} ','INFO',True)
        
        if len(list_repeat) > 0:
            for day in list_repeat:
                getattr(schedule.every(),day).at(hour).do(serv.case_job, global_time=global_time, **kwargs)
        

    def valid_hour(self, hour_sched, hour):
        if not hour is not None:
            return hour_sched
        return hour

    def valid_repeat(self, repeat_sched, repeat):
        if not repeat is not None:
            return repeat_sched
        return repeat

