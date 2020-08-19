
from vmanage.api.authentication import Authentication
# from vmanage.api.device_templates import DeviceTemplates
from vmanage.data.template_data import TemplateData
import pprint
import os

vmanage_host = os.environ.get('VMANAGE_HOST')
vmanage_username = os.environ.get('VMANAGE_USERNAME')
vmanage_password = os.environ.get('VMANAGE_PASSWORD')
pp = pprint.PrettyPrinter(indent=2)

auth = Authentication(host=vmanage_host, user=vmanage_username, 
                            password=vmanage_password).login()
# device_templates = DeviceTemplates(auth, vmanage_host)
template_data = TemplateData(auth, vmanage_host)

# device_template_list = device_templates.get_device_template_list()
# pp.pprint(device_template_list)

exported_device_template_list = template_data.export_device_template_list()
pp.pprint(exported_device_template_list)