from email import header
from pi_functions import token_check, env_check, get_time, smart_startup_probe
import os


if __name__ == "__main__":
    print(f"{get_time()} **************** BEGINNING STARTUP SCRIPT ****************")
    env_check(env_list = [
        "API_URL",
        "VOICE_MONKEY_API_URL",
        "AUTO_SHUTDOWN_MONKEY",
        "VOICE_MONKEY_AUTO_SHUTDOWN_SECRET",
        "VOICE_MONKEY_AUTO_SHUTDOWN_TOKEN",
        "OCTOPI_TOKEN"
        ])
    headers = token_check()
    api_url = os.environ['API_URL']
    startup_success = smart_startup_probe(api_url, headers)
    if startup_success:
        print(f"{get_time()} - Successful startup")
