"""Parse Methods for Data Returned by Cisco vManage.
"""

VALID_STATUS_CODES = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]


class ParseMethods:
    """Reset all configuratios on a vManage instance.

    Executes the necessary REST calls in specific order to remove
    configurations applied to a vManage instance.

    """
    @staticmethod
    def parse_data(response):
        """Parse data and provide error handling for missing data.

        Args:
            response (obj): Requests response object

        Returns:
            result (dict): All data associated with a response.

        Raises:
            Exception: Provides error message and details of issue.
        """

        if response['json'] and 'data' in response['json']:
            result = response['json']['data']
        else:
            error = response['error']
            result = response['details']
            raise Exception(f'{error}: {result}')
        return result

    @staticmethod
    def parse_status(response):
        """Retrieve status code for transactions that do not receive
        a response.

        Args:
            response (obj): Requests response object

        Returns:
            result (dict): All data associated with a response.

        """
        if response['status_code'] in VALID_STATUS_CODES:
            result = response['status_code']
        else:
            status = response['status']
            result = response['status_code']
            raise RuntimeError(f'{status}: {result}')
        return result

    @staticmethod
    def parse_config(response):
        """Parse config and provide error handling for missing data.

        Args:
            response (obj): Requests response object

        Returns:
            result (dict): All data associated with a response.

        Raises:
            Exception: Provides error message and details of issue.
        """

        if response['json'] and 'config' in response['json']:
            result = response['json']['config']
        else:
            error = response['error']
            result = response['details']
            raise RuntimeError(f'{error}: {result}')
        return result

    @staticmethod
    def parse_id(response):
        """Parse id and provide error handling for missing data.

        Args:
            response (obj): Requests response object

        Returns:
            result (dict): All data associated with a response.

        Raises:
            Exception: Provides error message and details of issue.
        """

        if response['json'] and 'id' in response['json']:
            result = response['json']['id']
        else:
            error = response['error']
            result = response['details']
            raise RuntimeError(f'{error}: {result}')
        return result
