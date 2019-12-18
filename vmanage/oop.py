import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

STANDARD_JSON_HEADER = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}

session = requests.Session()
session.headers.update(STANDARD_JSON_HEADER)
base_url = ''

class GenericMethods:
    # TODO
    pass

class ErrorHandling:
    # TODO
    pass

class Authentication:

    def __init__(self, host=None, user=None, password=None, port=443,
                validate_certs=False, disable_warnings=False, timeout=10):
        """
        default constructor for vmanage_session class, initialize self variables
        """
        global base_url
        base_url = 'https://{0}:{1}/dataservice'.format(host, port)
        session.verify = validate_certs
        
        self.headers = dict()
        self.cookies = None
        self.json = None
        self.method = None
        self.path = None
        self.response = None
        self.status = None
        self.url = None
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.timeout = os.getenv('VMANAGE_TIMEOUT', timeout)
        self.base_url = 'https://{0}:{1}/dataservice'.format(host, port)
        self.policy_list_cache = {}
        self.login()
    
    def login(self):
        """
        login() authenticates user, obtains jsessionid and adds it to the header, then
        checks device version to determine if x-xsrf token is needed.  if token is 
        required the x-xsrf token is added to the session header.
        """
        
        # auth user, add cookie jsessionid to header
        try:
            response = session.post(
                url='{0}/j_security_check'.format(self.base_url),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={'j_username': self.user, 'j_password': self.password},
                timeout=self.timeout
            )
            if response.status_code != 200 or response.text.startswith('<html>'):
                raise Exception('Could not login to device, check user credentials.')
        except requests.exceptions.RequestException as e:
            raise Exception('Could not connect to {0}: {1}'.format(self.host, e))
        
        # check vmanage version to determine if x-xsrf token is needed
        try:
            response = session.get(
                url='https://{0}/dataservice/system/device/controllers?model=vmanage&&&&'.format(self.host),
                timeout=self.timeout
            )
            version = response.json()['data'][0]['version']
            if version >= '19.2.0':
                response = session.get(
                    url='https://{0}/dataservice/client/token'.format(self.host),
                    timeout=self.timeout
                )
                session.headers['X-XSRF-TOKEN'] = response.content
        except requests.exceptions.RequestException as e:
            raise Exception('Could not connect to {0}: {1}'.format(self.host, e))

    @staticmethod
    def end_session():
        #TODO
        pass
    
class SharedLists():

    @staticmethod
    def get_data_prefix_list():
        api = base_url + "/template/policy/list/dataprefix"
        response = session.get(api)
        return response.content

    @staticmethod
    def get_data_prefix_list_id_by_name(name):
        list_id = ''
        api = base_url + "/template/policy/list/dataprefix"
        response = session.get(api)
        data = response.json()['data']
        for entry in data:
            if entry["name"] == name:
                list_id = entry["listId"]        
        return list_id

    @staticmethod
    def get_data_prefix_list_name_by_id(list_id):
        list_name = ''
        api = base_url + "/template/policy/list/dataprefix"
        response = session.get(api)
        data = response.json()['data']
        for entry in data:
            if entry["listId"] == list_id:
                list_name = entry["name"]        
        return list_name

class CentralizedLists():
    #TODO    
    pass

class LocalizedLists():
    #TODO
    pass

class SecurityLists():
    #TODO
    pass

class CentralizedPolicy():
    
    @staticmethod
    def post_cflowd_policy(templateName, templateDescription):
        api = base_url + "/template/policy/definition/cflowd"
        
        templateType = "cflowd"
        
        templateDefinition = {
            "flowActiveTimeout":180,
            "flowInactiveTimeout":60,
            "flowSamplingInterval":180,
            "templateRefresh":180,
            "collectors":[]
        }
        
        payload = f"{{'name':'{templateName}','type':'{templateType}','description':'{templateDescription}',"\
                f"'definition':{templateDefinition}}}"     
        payload = payload.replace("\'", "\"")
        response = session.post(url=api, data=payload)
    
    @staticmethod
    def post_traffic_data_policy():
        pass

class LocalizedPolicy():
    #TODO
    pass

class SecurityPolicy():
    #TODO
    pass

class FeatureTemplates():
    #TODO
    pass

class DeviceTemplates():
    #TODO
    pass