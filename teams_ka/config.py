import argparse, base64, os
from configparser import ConfigParser
from teams_ka import helpers, crypto

class Default_Config:
  def __init__(self) -> None:

    # app
    self.verbose = True
    self.key = ''

    # account
    self.username = ''
    self.password = ''

    # browser
    self.interactive = False
    self.browserWidth = 70
    self.browserHeight = 444

    # session
    self.timeoutMultiplier = 1
    self.loginDelay = 30

    self.maxReconnects = 3
    self.maxMfaRetries = 3

    # user activity
    self.userReconnectDelay = 3
    self.refreshRate = 30

    # must be supplied via console or ini
    self.required = [
      'username',
      'password'
    ]

class Config:
  def __init__(self) -> None:

    # defaults
    self._app_defaults_ = Default_Config()
    self.__dict__.update(self._app_defaults_.__dict__)

    # parse ini
    self._ini_dict_ = self._readini_()
    self.__dict__.update(self._ini_dict_)

    # parse console args
    self._console_args_ = self._argparser_()
    self.__dict__.update(self._console_args_.__dict__)

    # update un and pw as needed
    if self.username and self.password:
      self._updateiniaccount_(self.username, self.password)

    # validate required arguments
    self.allReqsMet = True
    for req in self._app_defaults_.required:
      if not req in self.__dict__.keys() or self.__dict__[req] == None or self.__dict__[req] == '':
        self.allReqsMet = False
        print(f'Argument \'{req}\' must be supplied in under-siege.ini or as console argument!')
      continue


  def _argparser_(self):

    # get console options
    parser = argparse.ArgumentParser(description='teams-ka - MS Teams Keep-Alive!')
    parser.add_argument('-u', '--username', default=self.username, nargs='?', const=self.username, type=str, dest='username', help=f'REQUIRED MS Teams username')
    parser.add_argument('-p', '--password', default=self.password, nargs='?', const=self.password, type=str, dest='password', help=f'REQUIRED MS Teams password')

    parser.add_argument('-v', '--verbose', default=self.verbose, action='store_true', dest='verbose', help=f'increase logging to include debug messages (default {self.verbose})')
    parser.add_argument('-i', '--interactive', default=self.interactive, action='store_true', dest='interactive', help=f'launch user interactive browser windows (default {self.interactive})')
    parser.add_argument('-t', default=self.timeoutMultiplier, nargs='?', const=self.timeoutMultiplier, type=int, dest='timeoutMultiplier', help=f'multiply the default timeout for rendered UI elements on the RD Web page (default {self.timeoutMultiplier})')
    parser.add_argument('-D', '--logindelay', default=self.loginDelay, nargs='?', const=self.loginDelay, type=int, dest='loginDelay', help=f'delay between initializing user logins (default {self.loginDelay})')
    parser.add_argument('-r', '--refreshrate', default=self.refreshRate, nargs='?', const=self.refreshRate, type=int, dest='refreshRate', help=f'delay between checking session alive and sending keepalive key (default {self.refreshRate})')

    return parser.parse_args()


  def _updateiniaccount_(self, username, password):
    iniPath = self._getinipath_()
      
    # get config
    config = ConfigParser()
    if os.path.exists(iniPath):
      config.read(iniPath)
    else:
      config = self._createini_(config, iniPath)

    b64key = config.get('app', 'key')
    key = crypto.fromBase64String(b64key)
    if not key:
      key = crypto.generateKey()
      config.set('app', 'key', crypto.toBase64String(key))
    b64pw = crypto.encryptWithKeyToBase64(key, password)

    config.set('account', 'username', username)
    config.set('account', 'password', b64pw)
    
    self._writeini_(config, iniPath)


  def _updateinikey_(self, key):
    iniPath = self._getinipath_()
      
    # get config
    config = ConfigParser()
    if os.path.exists(iniPath):
      config.read(iniPath)
    else:
      config = self._createini_(config, iniPath)
    config.set('app', 'key', key)

    self._writeini_(config, iniPath)


  def _writeini_(self, config, iniPath):
    # write file
    with open(iniPath, 'w') as configfile:
      config.write(configfile)
    

  def _createini_(self, config, iniPath):

    # encrypt password
    encoded = lambda:0
    encoded.key = ''
    encoded.data = ''
    if self.password:
      encoded = crypto.encryptToBase64(self.password)
    
    # app
    config.add_section('app')
    config.set('app', 'verbose', 'False')
    config.set('app', 'key', encoded.key)

    # account
    config.add_section('account')
    config.set('account', 'username', self.username)
    config.set('account', 'password', encoded.data)

    # session
    config.add_section('session')
    config.set('session', 'timeoutMultiplier', str(self.timeoutMultiplier))
    config.set('session', 'loginDelay', str(self.loginDelay))
    config.set('session', 'maxReconnects', str(self.maxReconnects))
    config.set('session', 'maxMfaRetries', str(self.maxMfaRetries))

    # browser
    config.add_section('browser')
    config.set('browser', 'interactive', str(self.interactive))
    config.set('browser', 'browserWidth', str(self.browserWidth))
    config.set('browser', 'browserHeight', str(self.browserHeight))

    # user
    config.add_section('user')
    config.set('user', 'userReconnectDelay', str(self.userReconnectDelay))
    config.set('user', 'refreshRate', str(self.refreshRate))

    # write file
    self._writeini_(config, iniPath)

    return config
    

  def _getinipath_(self):
    
    iniFilename = 'teams-ka.ini'

    # determine root path (for debugging)
    if helpers.amDebugging:
      return f'{os.path.dirname(os.path.realpath(__file__))}/../{iniFilename}'
    else:
      return iniFilename

    
  def _getiniconfig_(self, iniPath):
    config = ConfigParser()
    if os.path.exists(iniPath):
      return config.read(iniPath)
    else:
      return self._createini_(config, iniPath)


  def _readini_(self):

    # get ini path
    iniPath = self._getinipath_()
      
    # get config
    config = ConfigParser()
    if os.path.exists(iniPath):
      config.read(iniPath)
    else:
      config = self._createini_(config, iniPath)


    dict = {
      'verbose': config.getboolean('app', 'verbose'),
      'key': config.get('app', 'key'),
      'username': config.get('account', 'username'),
      'password': config.get('account', 'password'),
      'timeoutMultiplier': config.getint('session', 'timeoutMultiplier'),
      'loginDelay': config.getint('session', 'loginDelay'),
      'maxReconnects': config.getint('session', 'maxReconnects'),
      'maxMfaRetries': config.getint('session', 'maxMfaRetries'),
      'interactive': config.getboolean('browser', 'interactive'),
      'browserWidth': config.getint('browser', 'browserWidth'),
      'browserHeight': config.getint('browser', 'browserHeight'),
      'userReconnectDelay': config.getint('user', 'userReconnectDelay'),
      'refreshRate': config.getint('user', 'refreshRate'),
    }

    # decrypt password if we have a key and password
    if dict['key'] and dict['password']:
      dict['password'] = crypto.decryptWithKeyFromBase64(dict['key'], dict['password'])

    # if no key then assume password is clear text, create key and encrypt password
    elif dict['password']:
      self._updateinikey_(crypto.generateKeyAsBase64())
      self._updateiniaccount_(dict['username'], dict['password'])

    return dict
