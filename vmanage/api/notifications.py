"""Cisco vManage Notifications API Methods.
"""

import time
from vmanage.api.http_methods import HttpMethods
from vmanage.data.parse_methods import ParseMethods


class Notifications(object):
    """Access to Various vManage Utilitiesinstance.

    vManage has several utilities that are needed for correct execution
    of applications against the API.  For example, this includes waiting
    for an action to complete before moving onto the next task.

    """
    def __init__(self, session, host, port=443):
        """Initialize Notifications object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'

    def get_notification_rules(self):
        """Provides notification rules

        Returns:
            result (dict): All data associated with a response.
        """

        api = "notifications/rules"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)
        return result

