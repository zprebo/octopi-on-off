from pi_functions import token_check, completed_job_listener, trigger_alexa_routine, env_check, get_time, shutdown_system
import os


if __name__ == "__main__":
    print(f"{get_time()} **************** BEGINNING NEW PRINT ****************")
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

    print(f"{get_time()} - Waiting for completed job...")
    job_completion = completed_job_listener(api_url, headers)
    if job_completion == 100.0:
        print(f"{get_time()} - Shutting Down Octoprint...")
        trigger_alexa_routine()
        time.sleep(10)
        shutdown_system(api_url, headers)
        exit(0)
