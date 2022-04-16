from functions import token_check, probe_server_up, restart_octoprint_server, shutdown_system
import time


if __name__ == "__main__":
    api_url = "http://octopi.local/api"
    headers = token_check()

    startup_timeout_threshold = 0
    successful_startup = False
    restart_threshold = 0
    failed_restart_cmd_threshold = 0
    
    while successful_startup == False:
        if restart_threshold > 3:
            shutdown_system(api_url, headers)
            raise Exception("429: Server was in safemode and failed to succssessfully start 3 times")
        health = probe_server_up(api_url, headers)
        while health['error'] == "incomplete startup":
            print("\nIncomplete Startup Received. Sleeping 15 seconds...")
            time.sleep(20)
            health = probe_server_up(api_url, headers)
            startup_timeout_threshold += 1
            if startup_timeout_threshold > 3:
                raise Exception("504: Timed out waiting for error code incomplete startup") 
        if health['status'] == "unhealthy" and health['error'] != "incomplete startup":
            print(f"\nSERVER ERROR: {health['error']}")
            print("\nRestarting Server...")
            restarted = restart_octoprint_server(api_url, headers)
            if restarted == False:
                while failed_restart_cmd_threshold < 4:
                    if failed_restart_cmd_threshold >= 3:
                        raise Exception("429: Failed to send restart command 3 times")
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
            successful_startup = True
    success_response = {
        'status_code': 200,
        'Message': 'Octoprint Server Successfully Started'
        }
    print(f"\n{success_response}")