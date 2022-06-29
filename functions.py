import requests
import os
import json
import time


def token_check():
    octopi_token = os.environ['OCTOPI_TOKEN']
    if octopi_token is None:
        raise ValueError("OCTOPI_TOKEN not set")
    else:
        headers = {"Authorization": f"Bearer {octopi_token}"}
    return headers

def probe_server_up(api_url, headers):
    server_up = False
    count = 0
    while server_up == False:
        try:
            r = requests.get(f"{api_url}/server", headers=headers)
            if b'502 Bad Gateway' not in r.content:
                server_up = True
            else:
                time.sleep(2)
        except:
            print("Server Unreachable...")
            time.sleep(2)
            if count < 45:
                count+=1
            else:
                raise Exception("504: Timed out probing server to come online")
    print("\nOctoprint Service Reachable...")
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


def probe_server_down(api_url, headers):
    server_up = True
    count = 0
    while server_up == True:
        try:
            r = requests.get(f"{api_url}/server", headers=headers)
            print(f"{r.status_code}: server still up")
            time.sleep(2)
            if count < 30:
                count+=1
            else:
                raise Exception("504: Timeout waiting for server to shutdown")
        except:
            server_up = False
    return server_up
    

def restart_octoprint_server(api_url, headers):
    api_call = f"{api_url}/system/commands/core/restart"
    r = requests.post(api_call, headers=headers)
    if r.status_code == 204: #204 response is No Error
        print("\nRestarted Octoprint Server. Sleeping 15 seconds...")
        return True
    else:
        print("\nReceived Error Code Restarting Server... Trying Again")
        return False


def shutdown_system(api_url, headers):
    api_call = f"{api_url}/system/commands/core/shutdown"
    r = requests.post(api_call, headers=headers)
    if r.status_code == 204: #204 response is No Error
        print("\nShutdown Octopi System...")
        return True
    else:
        print("\nGot Error Shutting Down Octopi System...")
        return False


def get_possible_system_commands(api_call, headers):
    r = requests.get(api_call, headers=headers)
    response = json.loads(r.content.decode("utf-8"))
    return response
