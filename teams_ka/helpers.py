import os, sys
from configparser import ConfigParser


# info
amDebugging = bool(sys.gettrace())


def clear():
  os.system('cls' if os.name == 'nt' else 'clear')


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