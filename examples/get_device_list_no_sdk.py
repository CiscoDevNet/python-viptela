# The requests library is used to communicate with vManage.
import requests
# pprint is used to make the output more readable.  It is mainly used for
# illustration, but is also usefor for debugging and verbose presentation.
import pprint
# disable_warning from urllib3 dables the warnings from using the self-signed
# certificate used in vManage by default.  This is not using a trusted certificate
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# This is the information that we need to get to vManage and authenticate.  Although
# the port can be assumed, the username and password is needed to get an API token. 
vmanage_host = '192.133.178.240'
vmanage_port = '443'
vmanage_username = 'admin'
vmanage_password = 'admin'

# The base URL is is simply the vManage's IP address/hostname in URL format with
# optional port number
base_url = 'https://%s:%s'%(vmanage_host, vmanage_port)

# The session token is retrieved from the path '/j_security_check'. Since we are using
# the requests library, the token is added to subsequent calls
login_action = '/j_security_check'

# The username and password are passed in as part of the payload of the API call.
login_data = {'j_username' : vmanage_username, 'j_password' : vmanage_password}

# Combining the base URL with the path renders the end point from when we get
# and API token.
login_url = base_url + login_action

# Create the requests session object
session = requests.session()

# We make a POST call of the URL and data from above.  If the response is in
# HTML, it means that a login error has occurred
login_response = session.post(url=login_url, data=login_data, verify=False)
if b'<html>' in login_response.content:
    print ("Login Failed")
    exit(1)

# The XRSF Token is used to prevent cross-site request forgery attacks and is
# required in vmanage 19.X
xsrf_token_url = base_url + '/dataservice/client/token'

# Now GET the URL constructed above to retrieve the token.  If a successful
# return code is not received (i.e. 200), then an error was encountered
login_token = session.get(url=xsrf_token_url, verify=False)
if login_token.status_code == 200:
    if b'<html>' in login_token.content:
        print ("Login Token Failed")
        exit(1)
    
    session.headers['X-XSRF-TOKEN'] = login_token.content

# Finally, construct the URL required to retrive the known devices from vManage
device_url = base_url + '/dataservice/device'

# The device data is retrieved using a GET method.  If a successful
# return code is received (i.e. 200), we use the requests library built in
# mething to decode the JSON returned in the response.  If any other code
# is received, it is printed.
device_list = session.get(url=device_url, verify=False)
if device_list.status_code == 200:
    json_data = device_list.json()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint (json_data)
else:
    print (device_list.status_code)
    exit(1)
