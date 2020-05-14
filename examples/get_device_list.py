#!/usr/bin/env python

from vmanage.api.authentication import Authentication
from vmanage.api.device import Device
import pprint

username = 'admin'
password = 'admin'
host = 'XX.XX.XX.XX'

auth = Authentication(host=host, user=username, password=password).login()
vmanage_device = Device(auth, host)

device_status_list = vmanage_device.get_device_status_list()

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(device_status_list)
