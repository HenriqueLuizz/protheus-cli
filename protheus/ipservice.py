import json
import time
import sys
import os
import click
from string import Template
from ipsetup import Setup
from common import log
from ipcloud import Cloud
from ipbot import bot_protheus


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




