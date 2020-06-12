import os
import re
import sys
import time
import json
import click
import pprint
import schedule
import requests
import subprocess
from string import Template
from datetime import datetime

# ---------------------- COMMON -----------------------------------

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

# ---------------------- BOT -----------------------------------

def get_settings(key):
        with open('settings.json') as json_file:
            data = json.load(json_file)
            if key in data:
                return [True, data[key]]
            else:
                return [False]

def set_config(self, key, value):
        conf = {}

        with open('settings.json') as json_file:
            conf = json.load(json_file)
            conf.update(dict({key:value}))

        with open('settings.json', 'w') as json_read:
            json.dump(conf, json_read,indent=4)

        print(f'Arquivo de configuração alterado | chave: {key} , valor: {value}')

        return conf


def bot_protheus(bot_message):

  bot_info = get_settings('bot')
  
  if bot_info[0]:
    bot_token = bot_info[1].get('bot_token',None)
    bot_chatID = bot_info[1].get('bot_chatid',None)
  else:
    print('Configure as chaves bot_token e bot_chatid')
    return
  
  if bot_chatID is not None or bot_token is not None:
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()
  else:
    print('Configure as chaves bot_token e bot_chatid')
    return


def bot_get_group_id():
  bot_token = '1060967586:AAFeFcqD0SSks6gPF2TnCzagiQ-DK907Ocg'

  get_groups = f'https://api.telegram.org/bot{bot_token}/getUpdates'
  
  response = requests.get(get_groups)

  data = response.json()

  print(data['ok'])
  
  for d in data['result']:
    id_chat = d['message']['chat']['id']
    type_chat = d['message']['chat']['type']
    
    if type_chat == 'group':
      chat_name = d['message']['chat'].get('title', '')
    else:
      chat_name = d['message']['chat'].get('first_name', '')

    # id_name = d['message']['from'].get('id', '')
    # first_name = d['message']['from'].get('first_name')
    # text = d['message'].get('text','')
    # print(f'user id {id_name} - nome {first_name} - tipo {type_chat} - id_chat  {id_chat} - chat name  {chat_name} - Text {text}')
    
  return {'id_chat': id_chat, 'name': chat_name, 'type': type_chat}

if __name__ == "__main__":
  msg = ""
  bot_protheus(f'Alguem sabe pq me fui chamado pela classe {__name__} ?')

# ---------------------- CLOUD -----------------------------------


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


# ---------------------- FILES -----------------------------------

class Files:

  def __init__(self, name, path_master, path_slv):
    self.name = name
    self.path_master = path_master
    self.path_slv = path_slv
    
  def get_name(self):
    return self.name

  def get_path_master(self):
    return self.path_master

  def get_path_slv(self):
    return self.path_slv

  def set_name(self, name):
    self.name = name

  def set_path_master(self, path_master):
    self.path_master = path_master

  def set_path_slv(self, path_slv):
    self.path_slv = path_slv


  def need_update(self, auto_update=False,auto_create=False, force=False):
    name = self.get_name()
    path_master = self.get_path_master()
    path_slv = self.get_path_slv()
    
    path_master_full = os.path.join(path_master, name)
    
    if self.it_exists(path_master_full):
      
      update_list = []
      create_list = []
      
      date_master = os.path.getmtime(path_master_full)
      
      log(f'Ultima modificação do {name} em {path_master} - '+ datetime.fromtimestamp(date_master).strftime('%d/%m/%Y %H:%M:%S'),'INFO')
      
      for slv in path_slv:

        if os.path.exists(os.path.join(slv, name)):

          date_slv = os.path.getmtime(os.path.join(slv, name ))
          
          if date_slv < date_master or force:
            log(f'{name} desatualizado em {slv} - '+ datetime.fromtimestamp(date_slv).strftime('%d/%m/%Y %H:%M:%S'),'INFO')
            update_list.append(slv)
        else:
          log(f'O arquivo {name} não foi localizado em {slv}','WARN')
          create_list.append(slv)      

      if auto_update:
        for update in update_list:
          log(f'O arquivo {name} está sendo atualizado em {update}','INFO')
          self.copy_file(path_master, update, name)

      if auto_create:
        for create in create_list:
          log(f'O arquivo {name} está sendo criado em {create}','INFO')
          self.copy_file(path_master, create, name)
      
      if len(update_list) == 0:
        log(f'Todos os {name} estão atulizado','INFO')
        
      return update_list
    
    else:
      log(f'Diretório inválido {path_master_full}',"WARN")


  def it_exists(self, path):
    return os.path.exists(path)


  def copy_file(self, path_source, path_target, artifact):
    
    cp = os.path.join(path_source, artifact)
    
    if sys.platform == 'win32':
      # Windows
      os.popen(f'copy {cp} {path_target}')
      time.sleep(1)
    else:
      # Linux
      os.popen(f'cp {cp} {path_target}')


# ---------------------- OCI -----------------------------------

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

# ---------------------- SETUP -----------------------------------

class Service:

    def __init__(self, appserver_name, appserver_path, conns, alwaysup,alwaysdown):
        self.appserver_name = appserver_name
        self.appserver_path = appserver_path
        self.conns = conns
        self.alwaysup = alwaysup
        self.alwaysdown = alwaysdown

    def load(self):
        with open('settings.json') as json_file:
            data = json.load(json_file)
            self.appserver_name = data.get('appserver_name',None)
            self.appserver_path = data.get('appserver_path',None)
            self.conns = data.get('conns',None)
            self.alwaysup = data.get('alwaysup',None)
            self.alwaysdown = data.get('alwaysdown',None)
            

    def writerows(self, action: str, **kwargs):
        
        ip_instance = kwargs.get('ip', None)
        
        row = Template('$action server $conn \n')
        rowsbrokerfile = ""
        poolup = []
        pooldown = []

        global_time = kwargs.get('global_time',False)
        
        if action == 'disable':
            if len(self.alwaysup) > 0:
                poolup = self.alwaysup
            for appconn in self.conns:
                if not appconn in poolup:
                    if ip_instance is not None and not global_time:
                        temp = appconn.split(':')
                        
                        if ip_instance == temp[0]:
                            rowsbrokerfile += row.substitute(action=action ,conn=appconn)
                    else:
                        rowsbrokerfile += row.substitute(action=action ,conn=appconn)
        else:
            if len(self.alwaysdown) > 0:
                pooldown = self.alwaysdown
            for appconn in self.conns:
                if not appconn in pooldown:
                    if ip_instance is not None and not global_time:
                        temp = appconn.split(':')
                        
                        if ip_instance == temp[0]:
                            rowsbrokerfile += row.substitute(action=action ,conn=appconn)
                    else:
                        rowsbrokerfile += row.substitute(action=action ,conn=appconn)

        return rowsbrokerfile

    
    def totvs_broker_command(self, **kwargs):
        job = kwargs.get('job',None)
        name = kwargs.get('name',None)
        ip = kwargs.get('ip',None)

        self.load()
        if not self.appserver_path.endswith('/') and not self.appserver_path.endswith('\\'):
            bar = '/'
            if sys.platform.startswith('win32'):
                bar = '\\'
            self.appserver_path = self.appserver_path + bar

        log(f'{self.appserver_path}.TOTVS_BROKER_COMMAND')

        with open(self.appserver_path + '.TOTVS_BROKER_COMMAND', 'w') as broker_file:
            
            if job == 'enableservice':
                """Cria o arquivo enable no diretório do appserver."""                

                broker_file.write(self.writerows('enable', **kwargs))

                with open('.protheus', "w") as p_file:
                    p_file.write('enabled')

                log(f'Os serviços do servidor {name.upper()} ({ip}) estão sendo habilitados agora no Broker Protheus.','INFO',True)

            elif job == 'disableservice':
                """Cria o arquivo disable no diretório do appserver."""
                
                broker_file.write(self.writerows('disable', **kwargs))
                
                with open('.protheus', "w") as p_file:
                    p_file.write('disabled')

                log(f'Os serviços do servidor {name.upper()} ({ip}) estão sendo desabilitado agora no Broker Protheus.','INFO',True)

            else:
                """Opção invalida"""
                log(f'Foi solicitado gerar o arquivo TOTVS_BROKER_COMMAND, mas o {job} é uma opção invalida. Deve ser informado enableservice ou disableservice.','INFO')


    def case_job(self, **kwargs):
        
        if 'enableservice' == kwargs.get('job') or 'disableservice' == kwargs.get('job'):
            self.totvs_broker_command(**kwargs)
        else:
            cloud = object.__new__(Cloud)
            cloud.change_state(**kwargs)


    def info(self, setup: Setup):

        # Mostrar os serviços que estão sendo observado
        allconns = setup.get_conns()
        # Lista de Sempre ativo
        alwaysup = setup.get_alwaysup()
        # Lista de Sempre desativo
        alwaysdown = setup.get_alwaysdown()
        # Status dos serviço atual Habilitado ou Desabilitado

        status = 'none'
        
        if os.path.exists('.protheus'):
            with open('.protheus', "r") as p_file:
                status = p_file.read()
            

        if len(allconns) > 0:
            click.secho('Serviços que estão sendo observado:', bold=True)
            for conn in allconns:
                click.secho('REMOTE SERVER : ' + click.style(conn, bold=True), bold=False)

        if len(alwaysup) > 0:
            click.secho('Serviços listados para sempre ficar habilitado:', bold=True)
            for up in alwaysup:
                click.secho('REMOTE SERVER : ' + click.style(up, bold=True, fg='cyan'), bold=False)

        if len(alwaysdown) > 0:
            click.secho('Serviços listados para sempre ficar desabilitado:', bold=True)            
            for down in alwaysdown:
                click.secho('REMOTE SERVER : ' + click.style(down,bold=True, fg='red'), bold=False)
        
        if status == 'enabled':
            click.secho('Os serviços estão ' + click.style('habilitado',bold=True, fg='green') + ' agora.', bold=False)
        elif status == 'disable':
            click.secho('Os serviços estão ' + click.style('desabilitado',bold=True, fg='red') + ' agora.', bold=False)





# ---------------------- SETUP -----------------------------------


"""Classe de configuração do CLI INSPETOR PROTHEUS
"""
class Setup:


    def __init__(self, appserver_path, appserver_name, conns, alwaysup, alwaysdown, is_default=False ):
        self.appserver_path = appserver_path
        self.appserver_name = appserver_name
        self.conns = conns
        self.alwaysup = alwaysup
        self.alwaysdown = alwaysdown
        self.is_default = is_default


    def get_appserver_path(self):
        return self.appserver_path


    def set_appserver_path(self, path):
        self.appserver_path = path


    def get_appserver_name(self):
        return self.appserver_name


    def set_appserver_name(self, name):
        self.appserver_name = name


    def get_alwaysup(self):
        return self.alwaysup


    def set_alwaysup(self, alwaysup):
        self.alwaysup = alwaysup


    def get_alwaysdown(self):
        return self.alwaysdown


    def set_alwaysdown(self, alwaysdown):
        self.alwaysdown = alwaysdown


    def get_conns(self):
        return self.conns


    def set_conns(self, conns):
        self.conns = conns


    def get_ini_conns(self):
        list_conn = []
        path = os.path.join(self.get_appserver_path(), self.get_appserver_name())
        print(path)
        try:
            with open(path, "r+") as ini:
                file_ini = ini.read()
            
                filtro = file_ini.splitlines()
                for line_ini in filtro:
                    if line_ini.startswith('REMOTE_SERVER') :
                        temp = line_ini.split('=')
                        list_conn.append(temp[1].strip().replace(" ",":"))
        
        except FileNotFoundError:
            log('Erro ao tentar abrir o INI do BROKER, verifique as chaves APPSERVER_NAME e APPSERVER_PATH se estão corretas', 'ERROR')
            sys.exit("Arquivo de configuração do Broker não foi localizado!")
        except PermissionError:
            log('Erro ao tentar abrir o INI do BROKER, permissão negada', 'ERROR')
        finally:
            pass

        return list_conn            


    def set_config(self, key, value):
        conf = {}

        with open('settings.json') as json_file:
            conf = json.load(json_file)
            conf.update(dict({key:value}))

        with open('settings.json', 'w') as json_read:
            json.dump(conf, json_read,indent=4)

        return conf

    def get_config(self):
        conf = {}

        if not os.path.exists('settings.json'):
            self.sample_config()

        with open('settings.json') as json_file:
            conf = json.load(json_file)
        return conf
        
        
    def init_setup(self):
        init_data = {
            'appserver_path' : os.getcwd(),
            'appserver_name' : 'appserver.ini',
            'conns' : [],
            'alwaysup' : [],
            'alwaysdown' : [],
            "rpo_name" : "",
            "rpo_master" : "",
            "rpo_slave": []
        }
        with open('settings.json') as json_file:
            conf = json.load(json_file)
            conf.update(init_data)
        
        with open('settings.json', 'w') as json_read:
            json.dump(conf, json_read,indent=4)

        pass


    def load(self):

        data = self.get_config()
        
        self.appserver_path = data.get('appserver_path','')
        self.appserver_name = data.get('appserver_name','')
        self.conns = data.get('conns',[])
        self.alwaysup = data.get('alwaysup',[])
        self.alwaysdown = data.get('alwaysdown',[])

    def updata_conns(self):

        ips = self.get_ini_conns()
        self.set_conns(ips)
        self.set_config('conns',ips)

    def sample_config(self):
        sample = {
            "oci": [],
            "appserver_name": "appserver.ini",
            "appserver_path": os.getcwd(),
            "startinstance": "00:00",
            "stopinstance": "00:00",
            "enableservice": "00:00",
            "disableservice": "00:00",
            "repeat": "daily",
            "conns": [],
            "alwaysup": [],
            "alwaysdown": [],
            "rpo_name" : "",
            "rpo_master" : "",
            "rpo_slave": []
            }

        with open('settings.json', 'w') as json_read:
            json.dump(sample, json_read,indent=4)

# ---------------------- SCHEDULE -----------------------------------

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


# ---------------------- PROTHEUS MAIN -----------------------------------
ipset = object.__new__(Setup)
ipserv = object.__new__(Service)
ipcl = object.__new__(Cloud)
ipsch = object.__new__(Scheduler)
ipfile = object.__new__(Files)

ipset.load()
ipsch.load()

@click.group()
def cli():
    pass

# Grupos do CLI PROTHEUS
@cli.group()
def setup():
    pass

@cli.group()
def service():
    pass

@cli.group()
def instance():
    pass

@cli.group()
def sched():
    pass

@cli.group()
def update():
    pass

# COMANDOS POR GRUPOS

# GRUPO DE COMANDOS DO SETUP
@setup.command('config', 
                short_help='Configura o diretório do broker, lista de exceção', 
                help="Configura o diretório do broker, lista de conexão de appserver slave que sempre fica ativo")
def config():

    path = click.prompt('Informe o caminho absoluto do diretório do appserver Broker (/totvs/bin/broker_appserver)', type=click.Path())
    path = os.path.expanduser(path)

    while not os.path.exists(path):
        click.echo(f'Diretório não encontrado, verifique se foi digitado corretamente. \n appserver_path = {path}')
        path = click.prompt('Informe um diretório valido do appserver Broker (c:\\totvs\\bin\\broker_appserver)', type=click.Path())
        path = os.path.expanduser(path)
    
    if not path.endswith('/') and not path.endswith('\\'):
        bar = '/'
        if sys.platform.startswith('win32'):
            bar = '\\'
        path = path + bar
    
    ipset.set_appserver_path(path)
    ipset.set_config('appserver_path',path)
    
    name = click.prompt('Informe o nome do arquivo de ini appserver Broker.', type=str, default='appserver.ini',show_default=True)
    
    app_name = path + name

    while not os.path.exists(app_name):
        click.echo(f'O arquivo {name} não encontrado em {path}, verifique se foi digitado corretamente. \n')
        name = click.prompt('Informe o nome de arquivo válido do appserver Broker.', type=str)
        app_name = path + name

    ipset.set_appserver_name(name)
    ipset.set_config('appserver_name',name)

    ips = ipset.get_ini_conns()
    ipset.set_conns(ips)
    ipset.set_config('conns',ips)
    
    click.secho('Conexões de appserver pré-configuradas.',bold=True)
    for ip in ips:
        click.secho(f'REMOTE SERVER -> {ip} ')
    
    
    ipsativo = []
    if click.confirm('Deseja configurar agora a lista de ips que o PROTHEUS CLI ' + click.style('SEMPRE',bold=True) +' deixará ativo?'):
        click.echo('Para a configuração correta deve respeitar a formatação [IP:PORTA] [192.168.0.1:1234]')
        
        ip = click.prompt('Informe o ip e porta do serviço que sempre ficará habilitado: ', type=str)
        
        ipsativo.append(ip)
        
        while click.confirm('Deseja adicinar mais IPs?'):
            ip = click.prompt('Informe o IP e PORTA do serviço: ', type=str)
            ipsativo.append(ip)

        for ipativo in ipsativo:
            click.secho(f'REMOTE SERVER -> {ipativo} ')
        
        if click.confirm('Confirma a gravação dos IPs acima?'):
            ipset.set_alwaysup(ipsativo)
            ipset.set_config('alwaysup',ipsativo)           
        else:
            click.echo('Configuração de descartada.')

    # if click.confirm('Deseja configurar agora a lista de ips que o PROTHEUS CLI ' + click.style('NUNCA',bold=True) +' irá ativar?'):
    #     print('quero')
    #     pass

    # if click.confirm('Deseja configurar manualmente a lista de ips que o PROTHEUS CLI irá gerenciar?'):
    #     print('quero')
    #     pass


@setup.command('init', 
                short_help='Inicializa ou zera o arquivo settings.json', 
                help="Inicializa ou zer o arquivo settings.json que é responsável pelos parâmetros do PROTHEUS CLI")
def init():
    appdir = os.getcwd()
    ipset.init_setup()
    click.echo(f'Arquivo de configuração settings.json foi criado em {appdir} .')


@setup.command('list',short_help='Lista os configurações do arquivo settings.json', help="Lista as configurações do arquivo settings.json")
def list_setup():
    data_config = ipset.get_config()
    click.secho('Arquivo de configuração do Protheus CLI', bold=True)
    pprint.pprint(data_config, indent=4)


# GRUPO DE COMANDOS DO SERVICE
@service.command('enable', 
                short_help='Habilita os serviços no broker protheus', 
                help="Cria o arquivo .TOTVS_BROKER_COMMAND como todas as conexões de appserver configurado no appserver.ini do broker, exceto as conexões listada na chave ALWAYSUP no SETTINGS.JSON. \n\nTemplate do conteudo do arquivo: enable server 127.0.0.1:1234", 
                epilog='')
def enable():
    
    click.echo('Habilitando serviços...')
    # Atualiza a lista de IP com a lista do appserver.ini
    ipset.updata_conns()

    ipserv.enable_broker(ipset)


@service.command('disable', 
                short_help='Desabilita os serviços no broker protheus', 
                help="Cria o arquivo .TOTVS_BROKER_COMMAND como todas as conexões de appserver configurado no appserver.ini do broker, exceto as conexões listada na chave ALWAYSDOWN no SETTINGS.JSON. \n\nTemplate do conteudo do arquivo: disable server 127.0.0.1:1234", 
                epilog='')
def disable():
    click.echo('Desabilitando serviços...')

    # Atualiza a lista de IP com a lista do appserver.ini
    ipset.updata_conns()

    ipserv.disable_broker(ipset)


@service.command('list', 
                short_help='Lista todos os serviços no BROKER PROTHEUS', 
                help="Lista todos os serviços configurados no APPSERVER.INI do broker e as listas de exceções ALWAYSUP e ALWAYSDOWN do SETTINGS.JSON.", 
                epilog='')
def list_service():
    ipserv.info(ipset)


# GRUPO DE COMANDOS DO INSTANCE
@instance.command('start',
                short_help='Inicia todas as instâncias. \n\n--quiet (quiet mode)', 
                help="Inicia todas as instâncias configuradas no SETTINGS.JSON, envia um sinal de START para cada instância", 
                epilog='')
@click.option('--quiet','-q',
                is_flag=True, 
                default=False, 
                help='modo sem interação, o sinal de START será enviado sem solicitar confirmação')
def start(quiet):    
    clouds = ipcl.identifyCloud()
    
    for c in clouds:
        if quiet:

            click.echo(f'As instâncias da {c.upper()} serão iniciadas agora!')
            
            if c == 'oci':
                oci_config = ipcl.get_oci()
                
                for config in oci_config:
                    ipcl.oci(ip=config.get('ip'),job='startinstance')
            else:
                log(f'Sorry, {c.upper()} not yet supported!')

        else:
            if click.confirm(f'Deseja iniciar as instâncias da {c.upper()} agora?'):
                if c == 'oci':
                    oci_config = ipcl.get_oci()
                    for config in oci_config:
                        ipcl.oci(ip=config.get('ip'),job='startinstance')
                else:
                    log(f'Sorry, {c.upper()} not yet supported!')


@instance.command('stop',
                short_help='Desliga todas as instâncias. \n\n--quiet (quiet mode)', 
                help="Desliga todas as instâncias configuradas no SETTINGS.JSON, envia um sinal de STOP para cada instância", 
                epilog='')
@click.option('--quiet','-q',
                is_flag=True,
                default=False,
                help='modo sem interação, o sinal de STOP será enviado sem solicitar confirmação')
def stop(quiet):
    
    clouds = ipcl.identifyCloud()

    for c in clouds:
        if quiet:

            click.echo(f'As instâncias da {c.upper()} serão paradas agora!')
            
            if c == 'oci':
                oci_config = ipcl.get_oci()
                for config in oci_config:
                    ipcl.oci(ip=config.get('ip'),job='stopinstance')
            else:
                log(f'Sorry, {c.upper()} not yet supported!')

        else:
            if click.confirm(f'Deseja desligar as instâncias da {c.upper()} agora?'):
                if c == 'oci':
                    oci_config = ipcl.get_oci()
                    for config in oci_config:
                        ipcl.oci(ip=config.get('ip'),job='stopinstance')
                else:
                    log(f'Sorry, {c.upper()} not yet supported!')


@instance.command('get',
                short_help='Verifica o estado de todas instâncias', 
                help="verifica o estado de todas as instâncias configuradas no SETTINGS.JSON", 
                epilog='')
def get():
    clouds = ipcl.identifyCloud()

    for c in clouds:
        if c == 'oci':
            oci_config = ipcl.get_oci()
            for config in oci_config:
                ipcl.oci(ip=config.get('ip'),job='')
        else:
            log(f'Sorry, {c.upper()} not yet supported!')
    
@instance.command('add',
                short_help='Adiciona um novo ID de instância, \n\n--iid <ID> (silent mode)', 
                help="Adiciona um novo ID de instância no SETTINGS.JSON \n\n protheus instance add \n\n protheus instance add --iid <ID> \n\n protheus instance add --iid <ID> --iid <ID> ...", 
                epilog='', deprecated=True)
@click.option('--iid', multiple=True, help='ID da instância que será adicionado (silent mode)')
def add(iid):
    clouds = ipcl.identifyCloud()

    if len(iid) > 0:
        ipcl.set_oci(list(iid))
        return

    for c in clouds:
        if c == 'oci':
            iids = []

            iid = click.prompt('Informe o OCID da instância ', type=str)
            iids.append(iid)
            
            while click.confirm('Continuar adicionando OCIDs?'):
                iid = click.prompt('OCID ', type=str)
                iids.append(iid)
            
            ipcl.set_oci(iids)

        else:
            log(f'Sorry, {c.upper()} not yet supported!')


@instance.command('remove',
                short_help='Remove um ID de instância, \n\n--iid <ID> (silent mode)', 
                help="Remove um ID de instância no SETTINGS.JSON \n\n protheus instance remove \n\n protheus instance remove --iid <ID> \n\n protheus instance remove --iid <ID> --iid <ID> ...", 
                epilog='',deprecated=True)
@click.option('--iid',multiple=True,help='ID da instância que será removida (mode silent)')
def remove(iid):
    clouds = ipcl.identifyCloud()
    
    if len(iid) > 0:
        ipcl.remove_ocid(list(iid))
        return

    for c in clouds:
        if c == 'oci':
            iids = []

            ocids = ipcl.get_oci()
            if len(ocids) > 0:
                for ocid in ipcl.get_oci():
                    click.echo(f'OCID : {ocid}')
            else:
                click.echo('Não existe OCID para remove')
                return

            iid = click.prompt('Informe o OCID da instância ', type=str)
            iids.append(iid)
            
            while click.confirm('Continuar remoovendo OCIDs?'):
                iid = click.prompt('OCID ', type=str)
                iids.append(iid)
            
            ipcl.remove_ocid(iids)
        else:
            log(f'Sorry, {c.upper()} not yet supported!')

# GRUPO DE COMANDOS DO SCHEDULE
@sched.command('enableservice',
                short_help='Define um horário para o serviço ser habilitado no BROKER.', 
                help="Define um horário para o serviço ser habilitado no BROKER. \n\n protheus sched enableservice \n\n protheus sched enableservice --hour <00:00>", 
                epilog='')
@click.option('--hour','-h',multiple=False,help='Definir horário, formato: 00:00 (mode silent)')
def enableservice(hour):
    if hour is not None:
        r = re.compile('[0-9][0-9]:[0-9][0-9]')
        if r.match(hour) is not None:
            log(f'Horário configurado {hour}')
            ipsch.set_config('enableservice',hour)
            return

    hour = click.prompt('Qual horário os serviços seram habilitado?')
    ipsch.set_config('enableservice',hour)


@sched.command('disableservice',
                short_help='Define um horário para o serviço ser desabilitado no BROKER.', 
                help="Define um horário para o serviço ser desabilitado no BROKER. \n\n protheus sched disableservice \n\n protheus sched disableservice --hour <00:00> (silent mode)", 
                epilog='')
@click.option('--hour','-h',multiple=False,help='Definir horário, formato: 00:00 (mode silent)')
def disableservice(hour):
    if hour is not None:
        r = re.compile('[0-9][0-9]:[0-9][0-9]')
        if r.match(hour) is not None:
            log(f'Horário configurado {hour}')
            ipsch.set_config('disableservice',hour)
            return


    hour = click.prompt('Qual horário os serviços seram desabilitado?')
    ipsch.set_config('disableservice',hour)


@sched.command('startinstance',
                short_help='Define um horário para a instância ser ligada.', 
                help="Define um horário para a instância ser ligada. \n\n protheus sched startinstance \n\n protheus sched startinstance --hour <00:00> (silent mode)", 
                epilog='')
@click.option('--hour','-h',multiple=False,help='Definir horário, formato: 00:00 (mode silent)')
def turnon(hour):

    if hour is not None:
        r = re.compile('[0-9][0-9]:[0-9][0-9]')
        if r.match(hour) is not None:
            log(f'Horário configurado {hour}')
            ipsch.set_config('startinstance',hour)
            return

    hour = click.prompt('Qual horário as instâncias seram habilitada?')
    ipsch.set_config('startinstance',hour)

@sched.command('stopinstance',
                short_help='Define um horário para a instancia ser desligada',
                help="Define um horário para a instancia ser desligada. \n\n protheus sched stopinstance \n\n protheus sched stopinstance --hour <00:00> (silent mode)", 
                epilog='')
@click.option('--hour','-h',multiple=False,help='Definir horário, formato: 00:00 (mode silent)')
def turnoff(hour):
       
    if hour is not None:
        r = re.compile('[0-9][0-9]:[0-9][0-9]')
        if r.match(hour) is not None:
            log(f'Horário configurado {hour}')
            ipsch.set_config('stopinstance',hour)
            return

    hour = click.prompt('Qual horário as instâncias seram desabilitada?')
    ipsch.set_config('stopinstance',hour)
    
@sched.command('repeat',
                short_help='Define a recorrencia das execuções, por padrão é daily', 
                help="Define a recorrencia de ligar e desligar as instâncias e habilitar e desabilitar os serviços. \n\n protheus sched repeat \n\n protheus sched repeat --rec <daily|weeky> (silent mode)", 
                epilog='')
@click.option('--rec','-r',multiple=False,help='Definir recorrencia, formato: daily | weekly (mode silent)')
def repeat(rec):
    
    if rec is not None:
        if rec.lower() == 'daily' or rec.lower() == 'weekly':
            log(f'Recorrência configurada {rec}')
            ipsch.set_config('repeat',rec)
            return
    rec = click.prompt('Qual será a recorrência?', show_choices=True, type=click.Choice(['daily','workingdays']))
    ipsch.set_config('repeat',rec)

@sched.command('list',
                short_help='Lista as configurações do agendamento e os serviços alvo', 
                help="Lista as configurações do agendamento de ligar e desligar as instâncias e habilitar e desabilitar os serviços.", 
                epilog='')
def list_sched():
    ipsch.load()
    
    clouds = ipcl.identifyCloud()

    click.secho('Horários configurado: ', bold=True)
    click.secho('')
    click.secho(f'Instâncias {clouds[0].upper()}: ', bold=True)
    click.secho('Ligar às ' + click.style(ipsch.get_startinstance(), bold=True), bold=False)
    click.secho('Desligar às ' + click.style(ipsch.get_stopinstance(), bold=True), bold=False)
    click.secho('')
    click.secho('Serviços Protheus: ', bold=True)
    click.secho('Habilitar às ' + click.style(ipsch.get_enableservice(), bold=True), bold=False)
    click.secho('Desabilitar às ' + click.style(ipsch.get_disableservice(), bold=True), bold=False)
    click.secho('')
    click.secho('Recorrencia : ' + click.style(ipsch.get_repeat(), bold=True), bold=True)
    click.secho('')
    click.secho('Appeservers alvo : ', bold=True)
    ipserv.info(ipset)
    

    
@sched.command('run',
                short_help='Inicia o processo de agendamento', 
                help="Inicia o processo de agendamento, ao executar este comando este console ficará exclusivo para o agendamento. \n\nPara iniciar este processo como serviço verifique a documentação.", 
                epilog='')
@click.option('--instance/--by_instance', is_flag=True, required=False, default=False, help='Executa os agendamentos de todas as instancias (mode silent)')
# @click.option('--instance','-i', required=False, help='Executa os agendamentos de todas as instancias (mode silent)')
def run(**kwargs):

    if 'all_instance' in kwargs:
        all_instance = kwargs.get('all_instance')
        by_instance = kwargs.get('by_instance')

    if 'by_instance' in kwargs:
        by_instance = kwargs.get('by_instance')

    click.echo('Thread do agendador iniciado!')

    # TO DO : Executar uma verificação na cloud e validar as configurações
    
    oci_list = ipcl.get_oci()
    # jobs = ['enableservice']
    jobs = ['enableservice', 'disableservice', 'startinstance', 'stopinstance']
    
    for job in jobs:
        
        for i in range(len(oci_list)):
            oci_jobtime = oci_list[i].get(job,None)
            oci_repeat = oci_list[i].get('repeat',None)
            oci_ip = oci_list[i].get('ip',None)
            oci_name = oci_list[i].get('name',None)
        
            ipsch.set_schedule(ipserv,ip=oci_ip, name=oci_name, job=job, jobtime=oci_jobtime, repeat=oci_repeat)

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            log('Agendamento abortado pelo usuário!','WARN')
            break
        except:
            log('Processo do agendamento foi interrompido inesperadamente!','WARN')
            break


# GRUPO DE COMANDOS DO UPDATE
@update.command('rpo',
                short_help='Lista e atualiza os RPOs desatualizados do Protheus', 
                help="Atualiza os artefatos do Protheus. \n\n protheus update rpo (lista os RPOs desatualizados)", 
                epilog='')
@click.option('--update', '-u',is_flag=True, default=False, help='Confirma automaticamente a atualização de todos os RPOs desatualizados')
@click.option('--create','-c',is_flag=True, default=False, help='Confirma automaticamente a criação dos RPOs caso não seja encontrado no destino')
@click.option('--force','-f',is_flag=True, default=False, help='Força copiar o RPO do MASTER (origem) para os SLAVES (destino), independente da data de modificação. É necessário passar --update ou -u, caso contrário só irá listar os arquivo que serão atulizados')
def rpo(update, create, force):
    data_config = ipset.get_config()

    if data_config.get('rpo_name',False) and data_config.get('rpo_master',False) and data_config.get('rpo_slave',False):
        ipfile.set_name(data_config['rpo_name'])
        ipfile.set_path_master(data_config['rpo_master'])
        ipfile.set_path_slv(data_config['rpo_slave'])
    
        ipfile.need_update(update, create, force)
    else:
        path = os.path.realpath('settings.json')
        log(f'Configuração do RPO não localizado em {path}', 'ERROR')
        log(f'Configure as chaves: \n"rpo_name" : "tttp120.rpo", \n"rpo_master" : "/totvs/protheus/apo/", \n"rpo_slave": ["/totvs/protheus_slv1/apo/", "/totvs/protheus_slv2/apo/"]')


# SUBGRUPOS ADICIONADO AO GRUPO PRINCIPAL
cli.add_command(setup)
cli.add_command(service)
cli.add_command(instance)
cli.add_command(sched)

setup.add_command(config)
setup.add_command(init)
setup.add_command(list_setup)

service.add_command(enable)
service.add_command(disable)
service.add_command(list_service)

instance.add_command(start)
instance.add_command(stop)
instance.add_command(get)
# instance.add_command(add)
# instance.add_command(remove)

sched.add_command(enableservice)
sched.add_command(disableservice)
sched.add_command(turnon)
sched.add_command(turnoff)
sched.add_command(repeat)
sched.add_command(list_sched)
sched.add_command(run)

update.add_command(rpo)

if __name__ == "__main__":
    cli()
    