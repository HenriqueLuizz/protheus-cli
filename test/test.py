import unittest2 as unittest
from app import fatorial
import json
import uuid

import psutil
import datetime
import logging
import boto3
from botocore.exceptions import ClientError

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def data(title,text):
    conf = {}
    new_id = uuid.uuid4()
    date = datetime.datetime.now()

    with open('data.json') as json_file:
        conf = json.load(json_file)
        print(conf[0])
        conf[0].update({'uid':f'{new_id}','titleText':title,'mainText':text, 'updateDate':f'{date}' })

    with open('data.json', 'w') as json_read:
        json.dump(conf, json_read,indent=4)

    return conf


def test_memory():
    cpu_all = 0
    memory = psutil.virtual_memory()[2]
    core = psutil.cpu_count() 
    print(f'A memória atual é {memory}')
    print(core)
    
    for x in range(core):
        cpu_all = psutil.cpu_percent(interval=1) + cpu_all
        print(psutil.cpu_percent(interval=1))

    print(f'cpu {cpu_all}')
    
    cpu_all = cpu_all / core
    
    msg = f'O consumo de memória do servidor máster está em {memory} por cento e o consumo de cpu está em {round(cpu_all)} por cento.'

    print(msg)

    # data('Status do servidor Máster', msg)

    upload_file('data.json','oraculoskill','dados.json')

    
    # self.assertLessEqual(psutil.virtual_memory()[2], 60)
    

if __name__ == '__main__':
    test_memory()
