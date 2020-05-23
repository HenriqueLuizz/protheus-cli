import json
import subprocess
import common

def result_oci(d):
    if d['status']:
        o = json.loads(d['result'])
        
        if 'data' in o:
            name = o['data']['display-name']
            lifecycle = o['data']['lifecycle-state']
            print(f'{name} - {lifecycle}')
            return True

    else:
        print('Falha ao realizar a conexão com o OCI \n' + d['result'])
        return False


def check_oci(iids:list):
    for iid in iids:
        command=f'oci compute instance get --instance-id {iid}'
        data = common.run(command)
        if data['status']:
            result_oci(data)
            return True
        else:
            print('Falha ao realizar a conexão com o OCI \n' + data['result'])
            return False
        break
    

def instancie_oci(iids:list, action='get'):
    print(f'OCI operation {action} running... ')
    if action.lower() == 'start':
        
        for iid in iids:
            data = common.run(f'oci compute instance action --instance-id {iid} --action START')
            result_oci(data)

    elif action.lower() == 'stop':
        
        for iid in iids:
            data = common.run(f'oci compute instance action --instance-id {iid} --action STOP')
            result_oci(data)
    else:
        
        for iid in iids:
            data = common.run(f'oci compute instance get --instance-id {iid}')
            result_oci(data)


