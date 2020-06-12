# protheus-cli

Gerenciador de ambiente Protheus on-premise e cloud

Inspetor Protheus CLI é um gerenciador e agendador de tarefas para os serviços do Protheus.


O warmup foi construido com os recursos e bibliotecas disponíveis da linguagem Python, devido a facilidade de
manipulação em multplataformas e a compatibilidade entre bibliotecas externas, como sistemas de mensageria e assistentes virtuais.

A plicação hoje realiza o agendamento de iniciar e parar instancias (servidores em cloud) e habilitar e desabilitar serviços do Protheus com o Broker e encaminha todas as notificações atraves de um bot no Telegram. 

Por enquanto o warmup suporta apenas uma nuvem publica, mas vamos continuar evoluindo o projeto para suportar todas as nuvem e com isso vamos conseguir gerar blueprint da infra estrutura do cliente com auxilio do Terraform e Anseble que facilitará a migração de arquitetura entre nuvens e também o escalamento automático onde o bot irá fazer o deploy de uma instancia quando houver a necessidade.


## PROTHEUS SETUP

```sh
protheus setup config       # Configura o diretório do broker e lista de exceções
protheus setup list         # Lista as configurações
```

## PROTHEUS SERVICE

```sh
protheus service enable     # Habilita os serviços no broker protheus
protheus service disable    # Desabilita os serviços no broker protheus
protheus service list       # Lista todos os serviços no broker protheus
```

## PROTHEUS INSTANCE

```sh
protheus instance start     # Inicia todas as instâncias Slaves
protheus instance stop      # Deliga todas as instâncias Slaves
protheus instance get       # Verifica o estado das instâncias Slaves
protheus instance add       # Adiciona uma nova instância
protheus instance remove    # Remove uma instância
```

## PROTHEUS SCHED

```sh
protheus sched enableservice    # Define um horário para habilitar os serviços
protheus sched disableservice  # Deifine um horário para desativar os serviços
protheus sched startinstance   # Define um horário para habilitar as instâncias
protheus sched stopinstance # Define um horário para desativar os instâncias
protheus sched repeat    # Define a recorrência do agendamento
protheus sched list         # Lista as configurações do agendamento
protheus sched run          # Inicia o processo de monitoramento das tarefas
```

## PROHEUS UPDATE

```sh
protheus update rpo         # Lista e/ou atualiza os RPOs desatualizados do Protheus
```

## Arquivo de configuração (SETTINGS.JSON)

O arquivo settings.json é o arquivo responsável pelas principais configurações do CLI, abaixo um exemplo da estrutura do arquivo.

> Embreve receberá suporte as mais nuvem publica.

```json
{
    "oci": [
        {
            "ocid": "ocid.0000000",
            "ip": "10.171.0.1",
            "startinstance": "00:00",
            "stopinstance": "00:00",
            "enableservice": "00:00",
            "disableservice": "00:00",
            "repeat": "workingdays",
            "name": "server-master-1"
        }
    ],
    "appserver_name": "appserver.ini",
    "appserver_path": "D:\\TOTVS\\bundles\\totvs_master\\tec\\appserver\\",
    "startinstance": "00:00",
    "stopinstance": "00:00",
    "enableservice": "00:00",
    "disableservice": "00:00",
    "repeat": "daily",
    "conns": [
        "127.0.0.1:1234",
        "127.0.0.1:1235",
        "127.0.0.2:1234",
        "127.0.0.2:1235"
    ],
    "alwaysup": [
        "127.0.0.1:1234"
    ],
    "alwaysdown": [
        "127.0.0.2:1234"
    ],
    "rpo_name": "tttp120.rpo",
    "rpo_master": "D:\\DIRETORIO\\DO\\RPO\\apo",
    "rpo_slave": [
        "D:\\DIRETORIO\\DO\\SLAVE_1\\protheus\\apo",
        "D:\\DIRETORIO\\DO\\SLAVE_2\\protheus\\apo",
        "D:\\DIRETORIO\\DO\\SLAVE_3\\protheus\\apo"
    ],
    "bot": {
        "bot_token": "token_do_bot",
        "bot_chatid": "id_do_chat"
    }
}
```
