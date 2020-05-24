import json
import common
import ipoci

class Cloud:


    def __init__(self):
        pass


    def identifyCloud(self):
        with open('settings.json') as json_file:
            data = json.load(json_file)
            for cloud in ['oci','aws','azure','gcp']:
                if cloud in data:
                    return [cloud]

    def enable_instance(self):
        clouds = self.identifyCloud()

        for c in clouds:
            if c == 'oci':
                self.oci('START')
            else:
                print(f'Sorry, {c.upper()} not yet supported!')



    def disable_instance(self):
        clouds = self.identifyCloud()

        for c in clouds:
            if c == 'oci':
                self.oci('STOP')
            else:
                print(f'Sorry, {c.upper()} not yet supported!')



    def get_oci(self):
        with open('settings.json') as json_file:
            data = json.load(json_file)
            if 'oci' in data:
                return data['oci']
            else:
                return []


    def oci(self, action):
        ipoci.instancie_oci(self.get_oci(), action)


    def set_oci(self, iids):
        conf = {}

        with open('settings.json') as json_file:
            conf = json.load(json_file)
            
            for iid in iids:
                common.log(f'OCID {iid} adicionado.')
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
                        common.log(f'OCID {iid} removido.')
                        conf['oci'].remove(iid)

        with open('settings.json', 'w') as json_read:
            json.dump(conf, json_read,indent=4)

        return conf


    # def get_totvs(self):
    #     with open('settings.json') as json_file:
    #         data = json.load(json_file)
    #         if 'totvs' in data:
    #             return data['totvs']
    #         else:
    #             return []


    # def get_aws(self):
    #     with open('settings.json') as json_file:
    #         data = json.load(json_file)
    #         if 'aws' in data:
    #             return data['aws']
    #         else:
    #             return []


    # def get_azure(self):
    #     with open('settings.json') as json_file:
    #         data = json.load(json_file)
    #         if 'azure' in data:
    #             return data['azure']
    #         else:
    #             return []

    # def get_gcp(self):
    #     with open('settings.json') as json_file:
    #         data = json.load(json_file)
    #         if 'gcp' in data:
    #             return data['gcp']
    #         else:
    #             return []



