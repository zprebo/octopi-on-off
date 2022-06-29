from functions import token_check, probe_server_down, restart_octoprint_server, shutdown_system
import time
import os

if __name__ == "__main__":
    headers = token_check()
    api_url = os.environ['API_URL']

    shutdown = False
    failed_shutdown_cmd_threshold = 0

    while shutdown == False:
        if failed_shutdown_cmd_threshold >= 3:
            raise Exception("429: Failed to send shutdown command 3 times")
        shutdown = shutdown_system(api_url, headers)
        time.sleep(20)
        failed_shutdown_cmd_threshold += 1
        server_up = probe_server_down(api_url, headers)
        if server_up == False:
            break
    print("200: Successful shutdown")
