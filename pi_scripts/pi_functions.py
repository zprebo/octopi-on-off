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


def wait_for_done(api_url, headers, x = 1):
    while x==1:
        try:
            r = requests.get(f"{api_url}/job", headers=headers)
            response = json.loads(r.content.decode("utf-8"))
            job_completion = response['progress']['completion']
            print(f"{get_time()} - Job completion: {job_completion}%")
            if job_completion == 100.0:
                return job_completion
            else:
                print(f"{get_time()} - Going to sleep...")
                time.sleep(300)
        except:
            print(f"{get_time()} - Going to sleep...")
            time.sleep(300)


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
        raise Exception("504: Timeout")
