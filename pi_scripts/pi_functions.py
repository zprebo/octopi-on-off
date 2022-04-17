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
    #time.sleep(30)
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
                print(f"{get_time()} - Going to sleep for {int((time_left * .95)/60)} minutes...")
                time.sleep(int(time_left * 0.9))
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
            print(f"{get_time()} - Routine Triggered")
            exit(0)
        else:
            time.sleep(30)
            count += 1
    if count >=3:
        raise Exception(f"{get_time()} - 504: Timeout Triggering Alexa Routine")


def probe_server_down(api_url, headers):
    server_up = True
    count = 0
    while server_up == True:
        try:
            r = requests.get(f"{api_url}/server", headers=headers)
            print(f"{get_time()} - {r.status_code}: Octoprint Server Still Up")
            time.sleep(2)
            if count < 30:
                count+=1
            else:
                raise Exception(f"{get_time()} - 504: Timeout waiting for server to shutdown.")
        except:
            print(f"{get_time()} - Server Down...")
            server_up = False
    return server_up


def shutdown_system(api_url, headers):
    api_call = f"{api_url}/system/commands/core/shutdown"
    r = requests.post(api_call, headers=headers)
    if r.status_code == 204: #204 response is No Error
        print(f"{get_time()} - Shutdown Octopi and Octoprint Server.")
        return True
    else:
        print(f"{get_time()} - Error Shutting Down Octopi Server. Forced Shutdown with Alexa Routine")
        return False