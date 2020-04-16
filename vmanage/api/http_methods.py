"""HTTP Methods for RESTful API Services.

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

STANDARD_HEADERS = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}
STANDARD_TIMEOUT = 10
VALID_STATUS_CODES = [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]


class HttpMethods(object):
    """HTTP Methods for vManage API Interaction

    Provides a consistent interaction with the vManage REST API.  Contains
    error handling for common HTTP interaction issues.

    """
    def __init__(self, session, url):
        """Initialize HttpMethods object with session parameters.

        Args:
            session (obj): Requests Session object
            url (str): URL of the API service being called

        """

        self.session = session
        self.url = url

    def request(self, method, headers=None, payload=None, files=None):
        """Performs HTTP REST API Call.

        Args:
            method (str): DELETE, GET, POST, PUT
            headers (dict): Use standard vManage header provided in
                module or custom header for specific API interaction
            payload (str): A formatted string to be delivered to
                vManage via POST or PUT REST call
            file (obj): A file to be sent to vManage

        Returns:
            result (dict): A parsable dictionary containing the full
                response from vManage for an interaction

        Raises:
            JSONDecodeError: Payload format error.
            ConnectionError: Connection error.
            HTTPError: An HTTP error occurred.
            URLRequired: A valid URL is required to make a request.
            TooManyRedirects: Too many redirects.
            Timeout: The request timed out.
            RequestException: There was an ambiguous exception.

        """

        if headers is None:
            headers = STANDARD_HEADERS
        result = {}
        error = None
        data = None
        details = None
        result_json = None

        if payload:
            if isinstance(payload, str):
                data = payload.replace("\'", "\"")
            else:
                data = payload

        if files:
            headers = None

        try:
            response = self.session.request(method,
                                            self.url,
                                            headers=headers,
                                            files=files,
                                            data=data,
                                            timeout=STANDARD_TIMEOUT)

            if response.text:
                result_json = json.loads(response.text)

            if response.status_code not in VALID_STATUS_CODES:
                details = json.loads(response.text)['error']['details']
                error = json.loads(response.text)['error']['message']

            result = {
                'status_code': response.status_code,
                'status': requests.status_codes._codes[response.status_code][0],  #pylint: disable=protected-access
                'details': details,
                'error': error,
                'json': result_json,
                'response': response,
            }

        except json.JSONDecodeError as e:
            raise Exception(f'Payload format error: {e}')
        except requests.exceptions.ConnectionError as e:
            raise Exception(f'Connection error to {self.url}: {e}')
        except requests.exceptions.HTTPError as e:
            raise Exception(f'An HTTP error occurred: {e}')
        except requests.exceptions.URLRequired as e:
            raise Exception(f'A valid URL is required to make a request: {e}')
        except requests.exceptions.TooManyRedirects as e:
            raise Exception(f'Too many redirects: {e}')
        except requests.exceptions.Timeout as e:
            raise Exception(f'The request timed out: {e}')
        except requests.exceptions.RequestException as e:
            raise Exception(f'There was an ambiguous exception: {e}')

        return result
