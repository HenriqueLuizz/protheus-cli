# protheus-cli

Gerenciador de ambiente Protheus on-premise e cloud

Inspetor Protheus CLI é um gerenciador e agendador de tarefas para os serviços do Protheus.

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