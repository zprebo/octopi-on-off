from pi_functions import token_check, wait_for_done, trigger_alexa_routine
import os


if __name__ == "__main__":
    headers = token_check()
    api_url = os.environ['API_URL']
    print("Waiting for completed job...")
    job_completion = wait_for_done(api_url, headers)
    if job_completion == 100.0:
        print("Job Complete. Triggering Alexa Routine...")
        trigger_alexa_routine()
