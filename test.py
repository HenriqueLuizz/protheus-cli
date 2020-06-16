import unittest2 as unittest

from __future__ import print_function
import psutil
print(psutil.cpu_percent())
print(psutil.virtual_memory())  # physical memory usage
print('memory % used:', psutil.virtual_memory()[2])

class TestMemory():
  pass
