import logging, os, sys, time
from app import helpers
from app.browser import Browser
from app.config import Config
from app.constants import *
from app.lumberjack import Lumberjack
from app.navigator import Navigator
from app.teams import Teams


# load configuration, exiting if properties are missing
try: config = Config(config_json=open('./config.json')).config
except FileNotFoundError: config = Config().config

if config.get_missing_args():
    Config.print_help(default_values=config)
    for arg in config.get_missing_args():
        print(f'\nMissing required argument: {arg}')
    
    sys.exit(1)


# app logging
Lumberjack.global_init(timezone=time.localtime if helpers.am_debugging else time.gmtime, log_file=f'{APP_NAME}.log', log_level=config.log_level)
Lumberjack.update_library_levels(libraries=['requests', 'urllib3'], log_level=config.lib_log_level)
logger = Lumberjack(__file__, console_output=config.console_output)
logger.info(f'{APP_NAME} - {APP_DESCRIPTION}')


# browser
browser = Browser(config=config)
browser.open()


# navigator
navigator = Navigator(browser=browser)
navigator.start()


print()

