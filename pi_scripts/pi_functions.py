import os
import requests
import json
import time
from datetime import datetime, timedelta


def env_check(env_list):
    for env in env_list:
        if not os.getenv(env):
            raise ValueError(f"Environment Variable Not Set: {env}")


def token_check():
    octopi_token = os.environ['OCTOPI_TOKEN']
    if octopi_token is None:
        raise ValueError("OCTOPI_TOKEN not set")
    else:
        headers = {"Authorization": f"Bearer {octopi_token}"}
    return headers


def get_time():
    return str((datetime.now() - timedelta(hours=7)).strftime("%m/%d/%Y, %H:%M:%S"))


def completed_job_listener(api_url, headers, x = 1):
    while x==1:
        try:
            r = requests.get(f"{api_url}/job", headers=headers)
            response = json.loads(r.content.decode("utf-8"))
            job_completion = response['progress']['completion']
            time_left = response['progress']['printTimeLeft']
            if job_completion == None:
                print(f"{get_time()} - No Job Printing...")
            else:
                print(f"{get_time()} - Job completion: {round(job_completion, 2)}%")
            if job_completion == 100.0:
                return job_completion
            else:
                format_time = int((time_left * .95)/60)
                if format_time == 0:
                    print(f"{get_time()} - Going to sleep for {int(time_left)} seconds...")
                else:
                    print(f"{get_time()} - Going to sleep for {format_time} minutes...")
                time.sleep(int(time_left * 0.95))
        except:
            print(f"{get_time()} - Going to sleep for 2 minutes...")
            time.sleep(120)


def trigger_alexa_routine():
    access_token = os.environ['VOICE_MONKEY_AUTO_SHUTDOWN_TOKEN']
    secret_token = os.environ['VOICE_MONKEY_AUTO_SHUTDOWN_SECRET']
    monkey = os.environ["AUTO_SHUTDOWN_MONKEY"]
    v_m_api_url = os.environ['VOICE_MONKEY_API_URL']
    params = {
        'access_token': access_token,
        'secret_token': secret_token,
        'monkey': monkey
    }
    count = 0
    while count < 3:
        r = requests.get(v_m_api_url, params=params)
        response = json.loads(r.content.decode("utf-8"))
        if response['status'] == "success":
            print(f"{get_time()} - Alexa Routine Triggered Successfully...")
            return True
        else:
            time.sleep(30)
            count += 1
    if count >=3:
        raise Exception(f"{get_time()} - 504: Timeout Triggering Alexa Routine")


def shutdown_system(api_url, headers):
    api_call = f"{api_url}/system/commands/core/shutdown"
    r = requests.post(api_call, headers=headers)
    if r.status_code == 204: #204 response is No Error
        print(f"{get_time()} - Shutdown Octopi and Octoprint Server.")
        return True
    else:
        print(f"{get_time()} - Error Shutting Down Octopi Server. Forcing Shutdown with Alexa Routine")
        return False


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


def restart_octoprint_server(api_url, headers):
    api_call = f"{api_url}/system/commands/core/restart"
    r = requests.post(api_call, headers=headers)
    if r.status_code == 204: #204 response is No Error
        print("\nRestarted Octoprint Server. Sleeping 15 seconds...")
        return True
    else:
        print("\nReceived Error Code Restarting Server... Trying Again")
        return False


def smart_startup_probe(api_url, headers):
    startup_timeout_threshold = 0
    successful_startup = False
    restart_threshold = 0
    failed_restart_cmd_threshold = 0
    
    while successful_startup == False:
        if restart_threshold > 3:
            shutdown_system(api_url, headers)
            raise Exception(f"{get_time()} - 429: Server was in safemode and failed to succssessfully start 3 times")
        health = probe_server_up(api_url, headers)
        while health['error'] == "incomplete startup":
            print("\nIncomplete Startup Received. Sleeping 15 seconds...")
            time.sleep(15)
            health = probe_server_up(api_url, headers)
            startup_timeout_threshold += 1
            if startup_timeout_threshold > 3:
                raise Exception(f"{get_time()} - 504: Timed out waiting for error code incomplete startup") 
        if health['status'] == "unhealthy" and health['error'] != "incomplete startup":
            print(f"\nSERVER ERROR: {health['error']}")
            print("\nRestarting Server...")
            restarted = restart_octoprint_server(api_url, headers)
            if restarted == False:
                while failed_restart_cmd_threshold < 4:
                    if failed_restart_cmd_threshold >= 3:
                        raise Exception(f"{get_time()} - 429: Failed to send restart command 3 times")
                    restarted = restart_octoprint_server(api_url, headers)
                    time.sleep(30)
                    failed_restart_cmd_threshold += 1
                    health = probe_server_up(api_url, headers)
                    if health['status'] == "healthy":
                        successful_startup = True
                        break
            else:
                restart_threshold += 1
                time.sleep(20)    
        else:
            return True
