import datetime, os, requests, sys


# info
am_debugging = bool(sys.gettrace())


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def time_to_datetime(time:datetime.time, date:datetime.datetime=datetime.datetime.now()) -> datetime.datetime:
    return date.replace(hour=time.hour, minute=time.minute, second=time.second, microsecond=time.microsecond)


def notifyDiscord(webhook:str, msg:str, notifyEveryone:bool=True, logger=None) -> str:
    if notifyEveryone:
        msg = f'@everyone {msg}'

    try:
        requests.post(webhook, json={"content": msg})
    except Exception as error:
        return error


def centeredTitle(width):
    centered = ''
    for line in title().splitlines():
        centered += line.center(width)
    return centered


def title():
    return """
                       _       __          __            __     __   _____             
               /\     | |      \ \        / /     /\     \ \   / /  / ____|            
   ______     /  \    | |       \ \  /\  / /     /  \     \ \_/ /  | (___    ______    
  |______|   / /\ \   | |        \ \/  \/ /     / /\ \     \   /    \___ \  |______|   
            / ____ \  | |____     \  /\  /     / ____ \     | |     ____) |            
           /_/    \_\ |______|     \/  \/     /_/    \_\    |_|    |_____/             
            _        _             _____   _                   ____    _        ______ 
     /\     \ \    / /     /\     |_   _| | |          /\     |  _ \  | |      |  ____|
    /  \     \ \  / /     /  \      | |   | |         /  \    | |_) | | |      | |__   
   / /\ \     \ \/ /     / /\ \     | |   | |        / /\ \   |  _ <  | |      |  __|  
  / ____ \     \  /     / ____ \   _| |_  | |____   / ____ \  | |_) | | |____  | |____ 
 /_/    \_\     \/     /_/    \_\ |_____| |______| /_/    \_\ |____/  |______| |______|
                                                                                       
                                                                                       """
