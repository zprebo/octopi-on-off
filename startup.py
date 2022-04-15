from functions import token_check, probe_server, restart_octoprint_server, shutdown_system
import time


if __name__ == "__main__":
    headers = token_check(api_url, headers)
    api_url = "http://octopi.local/api"

    successful_startup = False
    restart_threshold = 4
    failed_restart_cmd_threshold = 0
    
    while successful_startup != True:
        if restart_threshold > 3:
            shutdown_system(api_url, headers)
            raise Exception("429: Server was in safemode and failed to succssessfully start 3 times")
        health = probe_server(api_url, headers)
        if health['status'] == "unhealthy":
            print(f"ERROR: {health['error']}")
            print("Restarting")
            restarted = restart_octoprint_server(api_url, headers)
            if restarted == False:
                while failed_restart_cmd_threshold < 4:
                    if failed_restart_cmd_threshold >= 3:
                        shutdown_system(api_url, headers)
                        raise Exception("429: Failed to send restart command 3 times")
                    restarted = restart_octoprint_server(api_url, headers)
                    time.sleep(30)
                    failed_restart_cmd_threshold += 1
                    health = probe_server(api_url, headers)
                    if health['status'] == "healthy":
                        successful_startup = True
                        break
            else:
                restart_threshold += 1      
        else:
            successful_startup = True

    if successful_startup == True:
        print("Successful Startup")