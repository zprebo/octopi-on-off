import requests
import os
import json
import time


def token_check(api_url, headers):
    octopi_token = os.environ['OCTOPI_TOKEN']
    if octopi_token is None:
        shutdown_system(api_url, headers)
        raise ValueError("OCTOPI_TOKEN not set")
    else:
        headers = {"Authorization": f"Bearer {octopi_token}"}
    return headers

def probe_server(api_url, headers):
    server_up = False
    count = 0
    while server_up != True:
        r = requests.get(f"{api_url}/server", headers=headers)
        if r.status_code == 200:
            server_up = True
        else:
            print("server not up")
            time.sleep(2)
            if count < 60:
                count+=1
            else:
                raise Exception("504: Timeout probing server")
    print("server up!")
    response = json.loads(r.content.decode("utf-8"))
    if not response['safemode'] or response['safemode'] == "False":
        health = {
            "status": "healthy",
            "error": "none"
        }
    else:
        health = {
            "status": "unhealthy",
            "error": f"{response['safemode']}"
        }
    return health


def restart_octoprint_server(api_url, headers):
    api_call = f"{api_url}/system/commands/core/restart"
    r = requests.post(api_call, headers=headers)
    if r.status_code == 204: #204 response is No Error
        print("restarted server")
        return True
    else:
        print("got error restarting server")
        return False


def shutdown_system(api_url, headers):
    api_call = f"{api_url}/system/commands/core/shutdown"
    r = requests.post(api_call, headers=headers)
    if r.status_code == 204: #204 response is No Error
        print("shutdown server")
        return True
    else:
        print("got error shutting down server")
        return False


def get_possible_system_commands(api_call, headers):
    r = requests.get(api_call, headers=headers)
    response = json.loads(r.content.decode("utf-8"))
    return response