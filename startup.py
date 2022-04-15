from functions import token_check, probe_server, restart_octoprint_server

if __name__ == "__main__":
    headers = token_check()
    api_url = "http://octopi.local/api"

    successful_startup = False
    restart_threshold = 0
    while successful_startup != True or restart_threshold <= 3:
        health = probe_server(api_url, headers)
        if health['status'] == "unhealthy":
            print(health['error'])
            restarted = False #restarted = restart_octoprint_server(api_url, headers)
            if restarted == False:
                print(health['error'])
                restarted = False #restarted = restart_octoprint_server(api_url, headers)
                if restarted == False:
                    print(health['error'])
                    restarted = False #restarted = restart_octoprint_server(api_url, headers)
                    if restarted == False:
                        print("Server was in safemode and failed to send restart command 3 times")
                        exit()
                else:
                    restart_threshold += 1
            else:
                restart_threshold += 1
        else:
            successful_startup = True

    if restart_threshold > 3 and successful_startup == False:
        print("Server was in safemode and failed to restart 3 times")
    if successful_startup == True:
        print("Successful Startup")