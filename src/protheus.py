import os
import re
import sys
import click
import pprint
import time
import schedule
from ipsetup import Setup
from ipservice import Service
from ipcloud import Cloud
from ipsched import Scheduler
from common import log, checkKey
from ipfiles import Files

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
    