import argparse, json
from app import crypto
from app.constants import APP_NAME, APP_DESCRIPTION
from app.lumberjack import Lumberjack
from dataclasses import dataclass

@dataclass
class Config_Options:

    # required settings
    required = ['username', 'password']

    # log settings
    # 10 = debug | 20 = info | 30 = warning | 40 = error | 50 = critical
    log_file: str = 'teams-ka.log'
    log_level: int = 20
    lib_log_level: int = 40
    gecko_log_level: int = 40
    console_output: bool = True

    # browser settings
    interactive: bool = True
    browser_width: int = 700
    browser_height: int = 600
    browser_pos_x: int = None
    browser_pos_y: int = None
    element_timeout: int = 5
    timeout_multiplier: float = 1
    selenium_logging_enabled: bool = True
    open_dev_tools: bool = False

    # auth settings
    key: str = None
    username: str = None
    password: str = None

    # teams settings
    teams_activity_interval: int = 60
    force_auth_app_notification: bool = False

    # discord settings
    discord_webhook_url: str = None
    discord_log_level: int = 0


    # returns any missing required args
    def get_missing_args(self) -> list[str]:
        items = []
        for item in self.required:
            if not self.__dict__[item]:
                items.append(item)

        return items


class Config:

    def __init__(self, config_json: str = None) -> None:
        self.config = Config_Options()
        
        # load values from config.json
        if config_json:
            config_file = json.load(config_json)
            for k in config_file.keys():
                if k in self.config.__dict__.keys():
                    self.config.__dict__[k] = config_file[k]

        # load arguments passed in console
        console_args = self._parse_args_()
        for a in [a for a in console_args.__dict__.keys() if console_args.__dict__[a]]:
            self.config.__dict__[a] = console_args.__dict__[a]
        
        # generate a new encryption key
        if not self.config.key and self.config.password:
            new_key = crypto.generateKey()
            self.config.key = crypto.toBase64String(new_key)

            # encrypt the clear text password (if exists)
            if self.config.password:
                self.config.password = crypto.encryptWithKeyToBase64(key=new_key, data=self.config.password)

        # encrypt and store pw sent via console
        if console_args.password:
            self.config.password = crypto.encryptWithKeyToBase64(key=crypto.fromBase64String(self.config.key), data=console_args.password)

        # create/update the config.json file
        self._update_config_file_()


    # get console options
    def _parse_args_(self):
        args, unknown = self._new_arg_parser_(self.config).parse_known_args()
        for u in unknown:
            print(f'Unknown Argument: {u}')
        return args

    # return a new argument parser
    @staticmethod
    def _new_arg_parser_(default_values: Config_Options=None) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=f'{APP_NAME} - {APP_DESCRIPTION}')
        parser.add_argument('-u', '--username', nargs='?', type=str, dest='username', help=f'username for user')
        parser.add_argument('-p', '--password', nargs='?', type=str, dest='password', help=f'password for user')
        parser.add_argument('-l', '--log_level', nargs='?', type=int, dest='log_level', help=f'40=ERROR | 20=INFO | 10=DEBUG (default: {default_values.log_level})')
        parser.add_argument('-i', '--interactive', action='store_true', dest='interactive', help=f'launch user interactive browser windows (default: {default_values.interactive})')
        parser.add_argument('-t', nargs='?', type=int, dest='timeout_multiplier', help=f'multiply the default timeout for rendered UI elements on the Web page (default: {default_values.timeout_multiplier})')
        return parser

    # print argument help
    @staticmethod
    def print_help(default_values: Config_Options=None) -> str:
        Config._new_arg_parser_(default_values=default_values).print_help()


    # create/update a confing.json file
    def _update_config_file_(self):
        with open('./config.json', 'w') as f:
            f.write(json.dumps(self.config.__dict__, indent=4))


    # create/update a confing.json file using the provided Config_Options class object
    @staticmethod
    def update_config_file(config_options: Config_Options=None):
        with open('./config.json', 'w') as f:
            f.write(json.dumps(config_options.__dict__, indent=4))
