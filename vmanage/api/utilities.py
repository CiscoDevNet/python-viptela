"""Cisco vManage Utilities API Methods.
"""

import time
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods


class Utilities(object):
    """Access to Various vManage Utilitiesinstance.

    vManage has several utilities that are needed for correct execution
    of applications against the API.  For example, this includes waiting
    for an action to complete before moving onto the next task.

    """
    def __init__(self, session, host, port=443):
        """Initialize Utilities object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'

    def get_active_count(self):
        """Provides number of active tasks on vManage.

        Returns:
            result (dict): All data associated with a response.
        """

        api = "device/action/status/tasks/activeCount"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

    def get_vmanage_version(self):
        api = 'system/device/controllers?model=vmanage&&&&'
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        version = result[0]['version']
        return version

    def get_action_status(self, action_id):
        response = {}
        action_status = None
        action_activity = None
        action_config = None
        url = f"{self.base_url}device/action/status/{action_id}"
        response = HttpMethods(self.session, url).request('GET')
        ParseMethods.parse_data(response)

        if 'json' in response:
            status = response['json']['summary']['status']
            if 'data' in response['json'] and response['json']['data']:
                action_status = response['json']['data'][0]['statusId']
                action_activity = response['json']['data'][0]['activity']
                if 'actionConfig' in response['json']['data'][0]:
                    action_config = response['json']['data'][0]['actionConfig']
                else:
                    action_config = None
            else:
                action_status = status
        else:
            raise Exception(msg="Unable to get action status: No response")

        return {
            'action_response': response['json'],
            'action_id': action_id,
            'action_status': action_status,
            'action_activity': action_activity,
            'action_config': action_config
        }

    def waitfor_action_completion(self, action_id):
        status = 'in_progress'
        response = {}
        action_status = None
        action_activity = None
        action_config = None
        while status == "in_progress":
            url = f"{self.base_url}device/action/status/{action_id}"
            response = HttpMethods(self.session, url).request('GET')
            ParseMethods.parse_data(response)

            if 'json' in response:
                status = response['json']['summary']['status']
                if 'data' in response['json'] and response['json']['data']:
                    action_status = response['json']['data'][0]['statusId']
                    action_activity = response['json']['data'][0]['activity']
                    if 'actionConfig' in response['json']['data'][0]:
                        action_config = response['json']['data'][0]['actionConfig']
                    else:
                        action_config = None
                else:
                    action_status = status
            else:
                raise Exception(msg="Unable to get action status: No response")
            time.sleep(10)

        return {
            'action_response': response['json'],
            'action_id': action_id,
            'action_status': action_status,
            'action_activity': action_activity,
            'action_config': action_config
        }

    def upload_file(self, input_file):
        """Upload a file to vManage.

        Args:
            input_file (str): The name of the file to upload.

        Returns:
            upload_status (str): The status of the file upload.
        """

        url = f"{self.base_url}system/device/fileupload"
        response = HttpMethods(self.session, url).request('POST',
                                                          files={'file': open(input_file, 'rb')},
                                                          payload={
                                                              'validity': 'valid',
                                                              'upload': 'true'
                                                          })
        ParseMethods.parse_status(response)
        return response['json']['vedgeListUploadStatus']
