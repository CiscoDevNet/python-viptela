"""Cisco vManage Centralized Policy API Methods.
"""
import json
import time

import dictdiffer
from vmanage.api.http_methods import HttpMethods
from vmanage.api.policy_definitions import PolicyDefinitions
from vmanage.data.parse_methods import ParseMethods
from vmanage.utils import list_to_dict


class CentralPolicy(object):
    """vManage Central Policy API

    Responsible for DELETE, GET, POST, PUT methods against vManage
    Central Policy.

    """
    def __init__(self, session, host, port=443):
        """Initialize Centralized Policy object with session parameters.

        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443

        """

        self.session = session
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/'
        self.policy_definitions = PolicyDefinitions(self.session, self.host)

    def activate_central_policy(self, policy_name, policy_id):
        """Activates the current active centralized policy

        Args:
            policyId (str): ID of the active centralized policy

        Returns:
            result (str): The Action ID from the activation.

        """

        url = f"{self.base_url}template/policy/vsmart/activate/{policy_id}?confirm=true"
        payload = {'policyName': policy_name}
        response = HttpMethods(self.session, url).request('POST', payload=json.dumps(payload))
        # result = ParseMethods.parse_status(response)
        if 'json' in response and 'id' in response['json']:
            return response['json']['id']

        error = response['error']
        result = response['details']
        raise Exception(f'{error}: {result}')

    def deactivate_central_policy(self, policy_id):
        """Deactivates the current active centralized policy

        Args:
            policyId (str): ID of the deactive centralized policy

        Returns:
            result (str): The Action ID from the activation.

        """

        url = f"{self.base_url}template/policy/vsmart/deactivate/{policy_id}?confirm=true"
        response = HttpMethods(self.session, url).request('POST')
        ParseMethods.parse_status(response)
        if 'json' in response and 'id' in response['json']:
            return response['json']['id']

        return None

    def add_central_policy(self, policy):
        """Delete a Central Policy from vManage.

        Args:
            policy: The Central Policy

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/vsmart"
        HttpMethods(self.session, url).request('POST', payload=json.dumps(policy))

    def update_central_policy(self, policy, policy_id):
        """Update a Central from vManage.

        Args:
            policy: The Central Policy
            policy_id: The ID of the Central Policy to update

        Returns:
            result (dict): All data associated with a response.

        """

        url = f"{self.base_url}template/policy/vsmart/{policy_id}"
        HttpMethods(self.session, url).request('PUT', payload=json.dumps(policy))

    def delete_central_policy(self, policyId):
        """Deletes the specified centralized policy

        Args:
            policyId (str): ID of the active centralized policy
        Returns:
            result (dict): All data associated with a response.

        """

        api = f"template/policy/vsmart/{policyId}"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('DELETE')
        result = ParseMethods.parse_status(response)
        return result

    def get_central_policy_list(self):
        """Get all Central Policies from vManage.

        Returns:
            response (dict): A list of all policy lists currently
                in vManage.

        """

        api = "template/policy/vsmart"
        url = self.base_url + api
        response = HttpMethods(self.session, url).request('GET')
        result = ParseMethods.parse_data(response)

        central_policy_list = result
        # We need to convert the policy definitions from JSON
        for policy in central_policy_list:
            try:
                json_policy = json.loads(policy['policyDefinition'])
                policy['policyDefinition'] = json_policy
            except Exception:  # TODO: figuring out better exception type to catch
                pass
            self.policy_definitions.convert_definition_id_to_name(policy['policyDefinition'])
        return central_policy_list

    def get_central_policy_dict(self, key_name='policyName', remove_key=False):

        central_policy_list = self.get_central_policy_list()

        return list_to_dict(central_policy_list, key_name, remove_key=remove_key)

    #pylint: disable=unused-argument
    def import_central_policy_list(self, central_policy_list, update=False, push=False, check_mode=False, force=False):
        central_policy_dict = self.get_central_policy_dict(remove_key=True)
        central_policy_updates = []
        for central_policy in central_policy_list:
            payload = {'policyName': central_policy['policyName']}
            payload['policyDescription'] = central_policy['policyDescription']
            payload['policyType'] = central_policy['policyType']
            payload['policyDefinition'] = central_policy['policyDefinition']
            if payload['policyName'] in central_policy_dict:
                # A policy by that name already exists
                existing_policy = central_policy_dict[payload['policyName']]
                diff = list(dictdiffer.diff(existing_policy['policyDefinition'], payload['policyDefinition']))
                if diff:
                    central_policy_updates.append({'name': central_policy['policyName'], 'diff': diff})
                if len(diff):
                    # Convert list and definition names to template IDs
                    if 'policyDefinition' in payload:
                        self.policy_definitions.convert_definition_name_to_id(payload['policyDefinition'])
                    if not check_mode and update:
                        self.update_central_policy(payload, existing_policy['policyId'])
            else:
                diff = list(dictdiffer.diff({}, payload['policyDefinition']))
                central_policy_updates.append({'name': central_policy['policyName'], 'diff': diff})
                if not check_mode:
                    # Convert list and definition names to template IDs
                    if 'policyDefinition' in payload:
                        self.policy_definitions.convert_definition_name_to_id(payload['policyDefinition'])
                    self.add_central_policy(payload)
        return central_policy_updates

    # Might want to move this later
    def waitfor_action_completion(self, action_id):
        status = 'in_progress'
        response = {}
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
                raise Exception(msg="Unable to get action status: No response")
            time.sleep(10)

        # if self.result['action_status'] == 'failure':
        #    self.fail_json(msg="Action failed")
        return {
            'action_response': response['json'],
            'action_id': action_id,
            'action_status': action_status,
            'action_activity': action_activity,
            'action_config': action_config
        }
