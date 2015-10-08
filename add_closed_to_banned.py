'''
Downloads all PR's from orthographic-pedant and any closed PR's
get added to the blacklist (we presume they don't want anymore fixes!).


'''
import requests, os

# Verify that there is a token set as an env variable and load it
shell_token  = "GITHUB_ORTHOGRAPHIC_TOKEN"
GITHUB_TOKEN = os.environ[shell_token]
login_params = {"access_token":GITHUB_TOKEN,}

API_URL = "https://api.github.com"
issues_url = API_URL + "/user/issues"

params = login_params.copy()

r = requests.get(issues_url, params=params)
print r
print r.content
print vars(r).keys()

'''
INTERFACE_API = 'https://github.com/pulls'
query_params = [
    "is:closed",
    "is:pr",
    "is:public",
    "author:orthographic-pedant",
]
query = ' '.join(query_params)
'''
