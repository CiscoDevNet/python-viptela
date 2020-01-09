"""Parse Methods for Data Returned by Cisco vManage.

MIT License

Copyright (c) 2019 Cisco Systems and/or its affiliates.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import requests

VALID_STATUS_CODES = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]


class ParseMethods():
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

        if 'data' in response['json']:
            result = response['json']['data']
        else:
            error = response['error']
            result = response['details']
            raise Exception(f'{error}: {result}')
        return(result)

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
            raise Exception(f'{status}: {result}')
        return(result)
