import os
import sys
import click
import pprint
import time
import schedule
from ipsetup import Setup
from ipservice import Service
from ipcloud import Cloud
from ipsched import Scheduler

ipset = object.__new__(Setup)
ipserv = object.__new__(Service)
ipcl = object.__new__(Cloud)
ipsch = object.__new__(Scheduler)

ipset.load()
ipsch.load()


@click.group()
# @click.option('-y', '--auto-confirm', 
#             default=False, 
#             is_flag=True, 
#             required=False, 
#             help='Habilita a confirmação automática.')
# @click.option('-q', '--squiet', default=False, is_flag=True, help='Executa sem interação com o usuário.')
# @click.option('-v', '--verbose', default=False, is_flag=True, help='Executa em modo verbose.')
# @click.option('-s', '--silent', default=False, is_flag=True, help='Executa em modo silencioso.')
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


# COMANDOS POR GRUPOS

# GRUPO DE COMANDOS DO SETUP
@setup.command()
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


@setup.command()
def init():
    appdir = os.getcwd()
    ipset.init_setup()
    click.echo(f'Arquivo de configuração settings.json foi criado em {appdir} .')


@setup.command()
def list():
    data_config = ipset.get_config()
    click.secho('Arquivo de configuração do Protheus CLI', bold=True)
    pprint.pprint(data_config, indent=4)


# GRUPO DE COMANDOS DO SERVICE
@service.command()
def enable():
    
    click.echo('Habilitando serviços...')
    # Atualiza a lista de IP com a lista do appserver.ini
    ipset.updata_conns()

    ipserv.enable_broker(ipset)


@service.command()
def disable():
    click.echo('Desabilitando serviços...')

    # Atualiza a lista de IP com a lista do appserver.ini
    ipset.updata_conns()

    ipserv.disable_broker(ipset)


@service.command()
def info():
    click.echo('service info')

    ipserv.info(ipset)


# GRUPO DE COMANDOS DO INSTANCE
@instance.command()
@click.option('--quiet',is_flag=True, default=False)
def poweron(quiet):
    
    clouds = ipcl.identifyCloud()

    for c in clouds:
        if quiet:

            click.echo(f'As instâncias da {c.upper()} serão paradas agora!')
            
            if c == 'oci':
                ipcl.oci('START')
            else:
                print(f'Sorry, {c.upper()} not yet supported!')

        else:
            if click.confirm(f'Deseja desligar as instâncias da {c.upper()} agora?'):
                if c == 'oci':
                    ipcl.oci('START')
                else:
                    print(f'Sorry, {c.upper()} not yet supported!')


@instance.command()
@click.option('--quiet',is_flag=True, default=False)
def poweroff(quiet):
    
    clouds = ipcl.identifyCloud()

    for c in clouds:
        if quiet:

            click.echo(f'As instâncias da {c.upper()} serão paradas agora!')
            
            if c == 'oci':
                ipcl.oci('STOP')
            else:
                print(f'Sorry, {c.upper()} not yet supported!')

        else:
            if click.confirm(f'Deseja desligar as instâncias da {c.upper()} agora?'):
                if c == 'oci':
                    ipcl.oci('STOP')
                else:
                    print(f'Sorry, {c.upper()} not yet supported!')


@instance.command()
def get():
    clouds = ipcl.identifyCloud()

    for c in clouds:
        if c == 'oci':
            ipcl.oci('GET')
        else:
            print(f'Sorry, {c.upper()} not yet supported!')
    

@instance.command()
def add():
    clouds = ipcl.identifyCloud()

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
            print(f'Sorry, {c.upper()} not yet supported!')

# GRUPO DE COMANDOS DO SCHEDULE
@sched.command()
def upservice():
    hour = click.prompt('Qual horário os serviços seram habilitado?')
    ipsch.set_config('upservice',hour)


@sched.command()
def downservice():
    hour = click.prompt('Qual horário os serviços seram desabilitado?')
    ipsch.set_config('downservice',hour)


@sched.command()
def turnon():
    hour = click.prompt('Qual horário as instâncias seram habilitada?')
    ipsch.set_config('upinstance',hour)


@sched.command()
def turnoff():
    hour = click.prompt('Qual horário as instâncias seram desabilitada?')
    ipsch.set_config('downinstance',hour)
    

@sched.command()
def recorence():
    rec = click.prompt('Qual será a recorencia?', show_choices=True, type=click.Choice(['daily','weekly']))
    ipsch.set_config('recorence',rec)


@sched.command()
def check():
    click.echo('schedule ckeck')


@sched.command()
def run():
    click.echo('Thread do agendador iniciado!')

    ipsch.enable_service(ipserv)
    ipsch.disable_service(ipserv)

    ipsch.enable_instance(ipcl)
    ipsch.disable_instance(ipcl)

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            print('Schedule aborted')
            break


cli.add_command(setup)
cli.add_command(service)
cli.add_command(instance)
cli.add_command(sched)

setup.add_command(config)
setup.add_command(init)
setup.add_command(list)

service.add_command(enable)
service.add_command(disable)
service.add_command(info)

instance.add_command(poweron)
instance.add_command(poweroff)
instance.add_command(get)
instance.add_command(add)

sched.add_command(upservice)
sched.add_command(downservice)
sched.add_command(turnon)
sched.add_command(turnoff)
sched.add_command(recorence)
sched.add_command(check)
sched.add_command(run)

if __name__ == "__main__":
    cli()
    