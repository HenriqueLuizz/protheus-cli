import os
import sys
import time
import json
import subprocess
from datetime import datetime
from common import log

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

