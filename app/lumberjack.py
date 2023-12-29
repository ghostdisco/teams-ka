import logging, os, sys, time
from logging import Logger

# Documentation from logging library
# CRITICAL = 50
# FATAL = CRITICAL
# ERROR = 40
# WARNING = 30
# WARN = WARNING
# INFO = 20
# DEBUG = 10
# NOTSET = 0

class Lumberjack:
    last_msg: str = None
    history: list[str] = []

    def __init__(self, filename:str=os.path.basename(__file__), custom_log_level:int=None, console_output:bool=True, retain_history:bool=False, capitalize_messages:bool=True) -> None:
        self.filename = os.path.basename(filename)
        self.console_output = console_output
        self.retain_history = retain_history
        self.capitalize_messages = capitalize_messages

        self.base = logging.getLogger(self.filename)

        if custom_log_level:
            self.base.setLevel(level=custom_log_level)


    # run once from __main__
    @staticmethod
    def global_init(timezone:time.struct_time=time.localtime, log_file:str='log.log', log_level:int=logging.INFO, format:str='%(asctime)s %(name)s %(levelname)s: %(message)s'):

        # initialize global instance of logger module
        logging.Formatter.converter = timezone
        logging.basicConfig(filename=log_file, level=log_level, format=format)

    # retrieve logger by name
    @staticmethod
    def get_logger(name:str) -> Logger:
        return logging.getLogger(name)

    # update log level of a list of libraries (i.e. requests)
    @staticmethod
    def update_library_levels(libraries:list[str]=[], log_level:int=logging.root.level):
        for l in libraries:
            Lumberjack.get_logger(name=l).setLevel(log_level)

    def critical(self, msg):
        self._log_(msg=msg, level=logging.CRITICAL)

    def error(self, msg):
        self._log_(msg=msg, level=logging.ERROR)

    def warning(self, msg):
        self._log_(msg=msg, level=logging.WARNING)

    def info(self, msg):
        self._log_(msg=msg, level=logging.INFO)

    def debug(self, msg):
        self._log_(msg=msg, level=logging.DEBUG)

    def _log_(self, msg:str, level:int):
        if logging.root.level <= 0 or logging.root.level > 50:
            return

        if self.capitalize_messages:
            msg = f'{msg[0].upper()}{msg[1:]}'

        if logging.root.level <= level:
            ext_msg = f'{self.filename} {logging.getLevelName(level)}: {msg}'
            self.last_msg = ext_msg
            
            if self.retain_history or self.console_output:
                if self.retain_history:
                    self.history.append(ext_msg)
                if self.console_output:
                    print(ext_msg)
        {
            logging.CRITICAL: self.base.critical,
            logging.ERROR: self.base.error,
            logging.WARNING: self.base.warning,
            logging.INFO: self.base.info,
            logging.DEBUG: self.base.debug
        }[level](msg)
        

        
