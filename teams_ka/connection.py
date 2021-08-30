import logging, random, time, os
import teams_ka.elements as Element
from enum import Enum
from teams_ka.models import User
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.remote_connection import LOGGER as gecko_logger


# logging
logger = logging.getLogger(__name__)
gecko_logger.setLevel(logging.ERROR)


###########################################################################
# region    ENUMS
###########################################################################
  
class Location(Enum):
  SIGNIN = 'signin'
  PASSWORD = 'password'
  STAYSIGNEDIN = 'staysignedin'
  WORKSPACES = 'workspaces'
  NORESOURCES = 'noresources'
  ALLOWRESOURCES = 'allowresources'
  OSLOGIN = 'oslogin'
  CONNECTED = 'connected'
  UNKNOWN = 'unknown'

class Status(Enum):
  PENDING = 'Pending'
  LOGGINGIN = 'Logging In'
  CONNECTING = 'Connecting'
  CONNECTED = 'Connected'
  DISCONNECTED = 'Disconnected'
  FAILED = 'Failed'
  CLOSED = 'Closed'
  TERMINATED = 'Terminated'

###########################################################################
# endregion
###########################################################################


###########################################################################
# region    CONNECTION
###########################################################################

class Connection:

  ###########################################################################
  # region    OPTIONS
  ###########################################################################

  class Options:

    # userReconnectDelay
    @property
    def userReconnectDelay(self): return self._userReconnectDelay
    @userReconnectDelay.setter
    def userReconnectDelay(self, value): self._userReconnectDelay = value

    # refreshRate
    @property
    def refreshRate(self): return self._refreshRate
    @refreshRate.setter
    def refreshRate(self, value): self._refreshRate = value

    # interactive
    @property
    def interactive(self): return self._interactive
    @interactive.setter
    def interactive(self, value): self._interactive = value

    # browserWidth
    @property
    def browserWidth(self): return self._browserWidth
    @browserWidth.setter
    def browserWidth(self, value): self._browserWidth = value

    # browserHeight
    @property
    def browserHeight(self): return self._browserHeight
    @browserHeight.setter
    def browserHeight(self, value): self._browserHeight = value

    # timeoutMultiplier
    @property
    def timeoutMultiplier(self): return self._timeoutMultiplier
    @timeoutMultiplier.setter
    def timeoutMultiplier(self, value): self._timeoutMultiplier = value

    # maxReconnects
    @property
    def maxReconnects(self): return self._maxReconnects
    @maxReconnects.setter
    def maxReconnects(self, value): self._maxReconnects = value

    # maxMfaRetries
    @property
    def maxMfaRetries(self): return self._maxMfaRetries
    @maxMfaRetries.setter
    def maxMfaRetries(self, value): self._maxMfaRetries = value


  ###########################################################################
  # endregion
  #
  # region    DEFAULT CONSTRUCTOR
  ###########################################################################

  def __init__(self, config) -> None:
    
    # options
    self.user = User(config.username, config.password)
    self.options = Options()
    self.options.userReconnectDelay = config.userReconnectDelay
    self.options.refreshRate = config.refreshRate
    self.options.interactive = config.interactive
    self.options.browserWidth = config.browserWidth
    self.options.browserHeight = config.browserHeight
    self.options.timeoutMultiplier = config.timeoutMultiplier
    self.options.maxReconnects = config.maxReconnects
    self.options.maxMfaRetries = config.maxMfaRetries

    # local properties
    self.status = Status.PENDING
    self.browser = webdriver.Firefox
    
    # initialize browser
    self.open()

  ###########################################################################
  # endregion
  #
  # region    HELPERS
  ###########################################################################
  
  def genCodeChallenge(self, sessionId):
    seed = sessionId.replace('-', '')
    E = 'E' if random.randint(0, 1) else '3'
    S = 'S' if random.randint(0, 1) else '5'
    I = 'I' if random.randint(0, 1) else '1'
    G = 'G' if random.randint(0, 1) else '6'
    return f'UND{E}R{S}{I}{E}{G}{E}n{seed}'

  @property
  def action(self):
    return self._action

  @action.setter
  def action(self, value, lvl=logging.INFO):
    self._action = f'{value[0].upper()}{value[1:]}'
    
    msg = value
    if bool(self.user.username):
      msg = f'{self.user.username} - {msg}'

    if lvl == logging.CRITICAL:
      logger.critical(msg)
    elif lvl == logging.ERROR:
      logger.error(msg)
    elif lvl == logging.WARNING:
      logger.warning(msg)
    elif lvl == logging.DEBUG:
      logger.debug(msg)
    else:
      logger.info(msg)

  @property
  def browserIsOpen(self):

    try:
      url = self.browser.current_url
      isOpen = bool(url)
      return isOpen
    except:
      return False

  ###########################################################################
  # endregion
  #
  # region    OPEN BROWSER
  ###########################################################################

  def open(self):
    
    # initialize browser
    opts = Options()
    if not self.options.interactive:
      opts.set_headless()
      assert opts.headless

    self.browser = webdriver.Firefox(options=opts, log_path=os.path.devnull, service_log_path=os.path.devnull)
    self.browser.set_window_size(self.options.browserWidth, self.options.browserHeight)
    
    self.action = f"Browser Initialized - {'Interactive' if self.options.interactive else 'Headless'} - {self.options.browserWidth}x{self.options.browserHeight}"
    self.action = f'ID: {self.browser.session_id}'

    return self.browserIsOpen

  ###########################################################################
  # endregion
  #
  # region    CLOSE BROWSER
  ###########################################################################

  def close(self):

    self.status = Status.CLOSED
    self.location = Location.UNKNOWN

    if self.browserIsOpen:
      self.browser.close()
      self.action = f"Browser Closed - ID: {self.browser.session_id}"

  def handleBrowserNotFound(self):

    self.close()

    if self.userReconnectDelay > -1:
      self.status = Status.PENDING
      time.sleep(self.userReconnectDelay)
      self.reconnect()
    else:
      self.status = Status.TERMINATED
      self.exit()

  def reconnect(self):
    self.close()
    self.open()
    self.start()

  ###########################################################################
  # endregion
  #
  # region    EXIT
  ###########################################################################

  def exit(self, reason='connection closed'):
    self.close()
    self.status = Status.TERMINATED
    self.location = Location.UNKNOWN
    self.action = reason
    return

  ###########################################################################
  # endregion
  #
  # region    START
  ###########################################################################

  def start(self):
    # initial connection
    self.connect()

    # reconnects
    i = 0
    while (i < self.options.maxReconnects):
      if not self.browserIsOpen: return False
      self.action = f"reconnecting"
      self.connect()
      i += 1

  ###########################################################################
  # endregion
  #
  # region    CONNECT
  ###########################################################################

  def connect(self):

    i = 1
    retries = 3
    while i <= retries:

      # return if no browser
      if not self.browserIsOpen:
        return Status.CLOSED
      
      self.login()
      # self.launchRd()

      if self.whereami() == Location.CONNECTED:
        break
      else:
        i += 1

    # return once status is DISCONNECTED
    self.status = Status.CONNECTED
    if self.whereami() == Location.CONNECTED:
      return self.watch(self.options.refreshRate)
    else:
      return Status.FAILED


  ###########################################################################
  # endregion
  #
  # region    WHEREAMI
  ###########################################################################
  def whereami(self):

    i = 1
    while i < 6:
      try:
        self.browser.find_element_by_id(Element.teamsButtonId)
        return Location.CONNECTED
      except: pass
      try:
        self.browser.find_element_by_id(Element.submitButtonId)
        return Location.STAYSIGNEDIN
      except: pass
      try:
        self.browser.find_element_by_name(Element.passwordBoxName)
        return Location.PASSWORD
      except: pass
      try:
        self.browser.find_element_by_name(Element.usernameBoxName)
        return Location.SIGNIN
      except: pass
      i += 1
    return Location.UNKNOWN

  ###########################################################################
  # endregion
  #
  # region    LOGIN
  ###########################################################################
  def loadSite(self):

    # url
    url = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize' + \
          '?client_id=5e3ce6c0-2b1f-4285-8d4b-75ee78787346' + \
          '&scope=openid%20profile' + \
          '&redirect_uri=https%3A%2F%2Fteams.microsoft.com%2Fgo' + \
          '&response_mode=fragment' + \
          '&response_type=id_token' + \
          '&x-client-SKU=MSAL.JS' + \
          '&x-client-VER=1.3.4' + \
          '&client_info=1' + \
          '&nonce=a3a1942b-3744-4543-b8de-5cd706591c9b' + \
          '&client-request-id=d89b28ce-6a41-4c1d-8845-ab69de40ba87' +\
          '&state=eyJpZCI6ImVhNTExMTZlLTYyNTMtNGY2Yy1hYTllLTRjOGY5MGY1ZWJmZSIsInRzIjoxNjMwMDkzNjExLCJtZXRob2QiOiJyZWRpcmVjdEludGVyYWN0aW9uIn0%3D'
    
    # load login page
    try:
      self.browser.get(url)
    except Exception as e:
      self.action = f'failed to load Teams: {e}'
      return False

    return True
    

  def submitUsername(self):

    # submit username form
    timeout = 5 * self.options.timeoutMultiplier
    try:
      WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.NAME, Element.usernameBoxName)))
      usernameForm = self.browser.find_element_by_name(Element.usernameBoxName)
      usernameForm.send_keys(self.user.username)
      submitBtn = self.browser.find_element_by_id(Element.submitButtonId)
      submitBtn.click()
    except:
      self.action = 'could not find username box'

      # check if user account cached in oauth SSO
      if not self.pickAnAccount():
        return False

    # wait for password form
    timeout = 5 * self.options.timeoutMultiplier
    try:
      WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.NAME, Element.passwordBoxName)))
      self.action = 'username accepted'
      return True
    except TimeoutException:
      self.action = 'username not accepted or password box not found'
      return False
    except Exception as e:
      if not self.browserIsOpen(): return False
      self.action = f'username not accepted or password box not found: {e}'
      return False

    
  def submitPassword(self):

    # enter password
    try:
      passwordForm = self.browser.find_element_by_name(Element.passwordBoxName)
      passwordForm.send_keys(self.user.password)
    except:
      self.action = 'could not find password box'
      return False

    # submit form
    timeout = 3 * self.options.timeoutMultiplier
    try:
      submitBtn = self.browser.find_element_by_id(Element.submitButtonId)
      submitBtn.click()

      # check for bad password
      WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.ID, Element.badPasswordId)))
      return False

      print()
    except:

      # exception means we couldn't find a bad password error
      return True

  
  def pickAnAccount(self):

    # check if user account cached in oauth SSO
    timeout = 5 * self.options.timeoutMultiplier
    try:
      WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.ID, Element.oauthCacheBoxId)))
      oauthCache = self.browser.find_element_by_id(Element.oauthCacheBoxId)
      usernameTile = oauthCache.find_elements_by_class_name('tile')[0]
      usernameTile.click()
      self.action = 'account is cached in oauth SSO'
    except:
      return False


  def awaitMfa(self):

    # await mfa
    timeout = 3 * self.options.timeoutMultiplier
    mfaWaitTime = 60
    try:
      WebDriverWait(self.browser, timeout).until_not(EC.presence_of_element_located((By.NAME, Element.passwordBoxName)))
      WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.ID, Element.mfaRequestId)))
      mfaTextElement = self.browser.find_element_by_id(Element.mfaRequestId)

      if (mfaTextElement.text == Element.mfaRequestText):
        self.action = 'password accepted'
        self.action = 'sent MFA request'
        self.action = 'awaiting MFA response'
        WebDriverWait(self.browser, mfaWaitTime).until_not(EC.presence_of_element_located((By.ID, Element.mfaRequestId)))
        self.action = 'received MFA response'
    except:
      pass


    # resend mfa
    timeout = 2 * self.options.timeoutMultiplier
    try:
      WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.ID, Element.mfaRequestResendButtonId)))
      mfaResendButton = self.browser.find_element_by_id(Element.mfaRequestResendButtonId)
      mfaResendButton.click()
      self.action = 'resending MFA request'
      return False

    except:
      pass


    # handle request to "Stay signed in"
    timeout = 3 * self.options.timeoutMultiplier
    try:
      WebDriverWait(self.browser, timeout).until_not(EC.presence_of_element_located((By.NAME, Element.passwordBoxName)))
      WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.ID, Element.submitButtonId)))
      submitBtn = self.browser.find_element_by_id(Element.submitButtonId)
      submitBtn.click()
      return True
    except TimeoutException:
      self.action = 'not asked to stay signed in'
      return False
    except:
      if not self.browserIsOpen: return False
      self.action = 'not asked to stay signed in'
      return False


  def login(self):

    self.status = Status.LOGGINGIN
    
    if not self.loadSite(): return False
    
    if not self.submitUsername(): return False

    if not self.submitPassword(): 
      self.options.maxReconnects = 0
      self.location = Location.UNKNOWN
      self.exit('bad password!')
      return False

    # if not self.passwordAccepted(): return False

    # retry mfa 3 times
    i = 0
    mfaSuccess = False
    while i < self.options.maxMfaRetries:
      if self.awaitMfa(): 
        mfaSuccess = True
        break
    if not mfaSuccess: return False

    # handle oauth cache click
    if not self.pickAnAccount(): pass
    
    # verify Teams loaded
    timeout = 20 * self.options.timeoutMultiplier
    try:
      self.status = Status.CONNECTING
      self.action = 'launching MS Teams'
      WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.ID, Element.teamsButtonId)))
      self.action = 'logged in successfully'
      return True
    except TimeoutException:
      self.status = Status.FAILED
      self.action = f'timed out waiting for Teams (timeout: {timeout})'
      return False
    except Exception as e:
      self.status = Status.FAILED
      if not self.browserIsOpen(): return False
      self.action = f'failed to load Teams: {e}'
      return False


  ###########################################################################
  # endregion
  #
  # region    TEAMS
  ###########################################################################
  


  ###########################################################################
  # endregion
  #
  # region    WATCH CONNECTION
  ###########################################################################

  def watch(self, refreshRate):

    self.action = 'watching connection'

    timeout = 10 * self.options.timeoutMultiplier
    while (1):

      # make sure we're connected and send keepalive key
      try:

        # check for Teams button
        WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.ID, Element.teamsButtonId)))
        
        self.keepAlive()

      except:

        # Teams button is missing
        self.action = '\'Teams\' button not found'
        self.status = Status.DISCONNECTED
        return Status.DISCONNECTED

      # wait for refreshTime to elapse
      try:

        # wait refreshTime to see if Teams button goes away
        WebDriverWait(self.browser, refreshRate).until_not(EC.element_to_be_clickable((By.ID, Element.teamsButtonId)))

        # wait timeout for Teams button to come back
        try:
          WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.ID, Element.teamsButtonId)))

          # still connected
          continue
        except:
          
          # Teams button is missing
          self.action = '\'Teams\' button not found'
          self.status = Status.DISCONNECTED
          return Status.DISCONNECTED

      except:
        
        # still connected
        continue



###########################
# BEGIN OLD CODE:
###########################


    # wait for element indicative of a disconnected session
    max = 20
    i = 1
    while (i < 20):
      i += 1
      try:

        self.action = 'watching connection'

        # wait for potential error modals
        WebDriverWait(self.browser, refreshRate).until_not(EC.element_to_be_clickable((By.ID, Element.teamsButtonId)))

        # teams not loaded
        try:
          # errorBox = self.browser.find_element_by_tag_name(Element.connectionErrorTagName)
          # error = errorBox.find_elements_by_tag_name('span')[0].text
          error = '\'Teams\' button not accessible'
          self.action = f'disconnected: {error}'
        except Exception as e:
          self.action = 'disconnected'
        
        return Status.DISCONNECTED

      except TimeoutException:
        
        # continue if no error modal found
        pass

      except Exception as e:
        if self.browserIsOpen: return False
        self.action = f'error: {e}'
        return Status.DISCONNECTED

      try:

        # check if teams button exists
        WebDriverWait(self.browser, 0).until(EC.element_to_be_clickable((By.ID, Element.teamsButtonId)))
        self.browser.find_element_by_id(Element.teamsButtonId)

        self.action = 'sending keepalive action'
        self.keepAlive()
            
      except:

        self.action = 'disconnected'
        return Status.DISCONNECTED

  ###########################################################################
  # endregion
  #
  # region    USER ACTIVITY
  ###########################################################################

  def keepAlive(self):

    # click Teams button
    button = self.browser.find_element_by_id(Element.teamsButtonId)
    button.click()

  ###########################################################################
  # endregion
  ###########################################################################


###########################################################################
# endregion
###########################################################################