import json
import os

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
        return self.appserver_path


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
        with open(self.appserver_path + self.appserver_name, "r+") as ini:
            file_ini = ini.read()
        
            filtro = file_ini.splitlines()
            for line_ini in filtro:
                if line_ini.startswith('REMOTE_SERVER') :
                    temp = line_ini.split('=')
                    list_conn.append(temp[1].strip().replace(" ",":"))

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
            "oci": [
                "ocid1.instance.oc1.iad.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "ocid1.instance.oc1.iad.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                ],
            "appserver_name": "appserver.ini",
            "appserver_path": os.getcwd(),
            "upinstance": "00:00",
            "downinstance": "00:00",
            "upservice": "00:00",
            "downservice": "00:00",
            "recorence": "daily",
            "conns": [],
            "alwaysup": [],
            "alwaysdown": [],
}
        with open('settings.json', 'w') as json_read:
            json.dump(sample, json_read,indent=4)



        