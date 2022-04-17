from pi_functions import token_check, wait_for_done, trigger_alexa_routine, env_check, get_time
import os


if __name__ == "__main__":
    env_list = [
        "API_URL",
        "VOICE_MONKEY_API_URL",
        "AUTO_SHUTDOWN_MONKEY",
        "VOICE_MONKEY_AUTO_SHUTDOWN_SECRET",
        "VOICE_MONKEY_AUTO_SHUTDOWN_TOKEN",
        "OCTOPI_TOKEN"
        ]
    env_check(env_list)

    # log with date time
    headers = token_check()
    api_url = os.environ['API_URL']
    print(f"{get_time()} - Waiting for completed job...")
    job_completion = wait_for_done(api_url, headers)
    if job_completion == 100.0:
        print(f"{get_time()} - Triggering Alexa Routine...")
        trigger_alexa_routine()
