import calendar, datetime, logging, math, time
from app import crypto
from app.browser import Browser
from app.config import Config
from app.constants import APP_NAME
from app.enums import *
from app.helpers import notifyDiscord
from app.lumberjack import Lumberjack
from app.teams import Teams
from dataclasses import dataclass
from enum import Enum
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.remote_connection import LOGGER as gecko_logger

# logging
logger: Lumberjack

@dataclass
class Navigator:

    class Status(Enum):
        READY = 'ready'
        PAUSED = 'paused'
        RUNNING = 'running'
        SUCCESS = 'success'
        FAILED = 'failed'
        TERMINATED = 'terminated'

        SIGN_IN = 'sign_in'
        TEAMS_APP = 'teams_app'
        TEAMS_APP_FAILED = 'teams_app_failed'

    ###########################################################################
    # region    DEFAULT CONSTRUCTOR
    ###########################################################################

    browser: Browser
    max_retries: int = 3
    time_between_retries: int = 5
    current_try: int = 0
    done: bool = False
    failed: bool = False
    exited: bool = True
    stopped: bool = False
    off_hours_url: str = 'https://www.google.com/'

    def __init__(self, browser: Browser) -> None:

        # logging
        global logger
        logger = Lumberjack(__file__, console_output=browser.config.console_output)

        self.browser = browser
        self.driver = browser.driver
        self.teams = Teams()
        self.status = Navigator.Status.READY

    ###########################################################################
    # endregion
    #
    # region    PUBLIC FUNCTIONS
    ###########################################################################

    def start(self):
        self.status = Navigator.Status.RUNNING

        while self.current_try < self.max_retries:

            if self.status != Navigator.Status.TEAMS_APP_FAILED:
                self.current_try += 1
                logger.info(f'Running: {self.current_try}/{self.max_retries}')
            else:
                logger.info(f'Re-running: {self.current_try}/{self.max_retries}')

            if self.status == Navigator.Status.FAILED:
                self._wait_(seconds=self.time_between_retries)

            self.status = Navigator.Status.RUNNING

            self._run_()

    def pause(self):
        self.status = Navigator.Status.PAUSED

    def terminate(self):
        self.status = Navigator.Status.TERMINATED

    ###########################################################################
    # endregion
    #
    # region    NOTIFICATIONS
    ###########################################################################

    def _notify_user_(self, msg:str=None, level:int=logging.INFO, force:bool=False):

        # discord
        if self.browser.config.discord_webhook_url:
            if force or level >= self.browser.config.discord_log_level:
                return notifyDiscord(webhook=self.browser.config.discord_webhook_url, msg=msg, notifyEveryone=force)

        # log
        logger._log_(msg=msg, level=logging.CRITICAL if force else level)

    ###########################################################################
    # endregion
    #
    # region    ENGINE
    ###########################################################################

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, status:Status):
        self._status = status
        logger.debug(f'nav status updated to: {status.value}')

    def _fail_(self, error: str=None):
        if error: self._notify_user_(msg=error, level=logging.ERROR)

        if Location.TEAMS_APP == self.location:
            self.status = Navigator.Status.TEAMS_APP_FAILED
        else:
            self.status = Navigator.Status.FAILED

    def _run_(self):
        try:
            if self.browser.status != Browser.Status.OPEN:
                logger.debug('opening browser')
                self.browser.open()

            while self.status == Navigator.Status.RUNNING:
                self._step_()
        except Exception as e:
            logger.error(f'an unexpected error has ocurred: {e}')

    def _step_(self):
        step = {
            Location.NEW_WINDOW: self._handle_teams_,
            Location.LOGIN: self._submit_username_,
            Location.PASSWORD: self._submit_password_,
            Location.PASSWORD_ALT: self._handle_password_alt_,
            Location.MFA: self._handle_mfa_,
            Location.MFA_OPTIONS: self._select_mfa_option_,
            Location.MFA_USER_PROMPT: self._prompt_user_,
            Location.MFA_RESEND_REQUEST: self._mfa_resend_request_,
            Location.STAY_SIGNED_IN: self._stay_signed_in_,
            Location.PICK_AN_ACCOUNT: self._pick_an_account_,
            Location.USE_WEB_APP_PROMPT: self._handle_use_web_app_prompt_,
            Location.TEAMS_APP_LOADING: self._wait_for_teams_load_,
            Location.TEAMS_APP: self._handle_teams_,
            Location.OFF_HOURS_SITE: self._handle_teams_,
            Location.UNKNOWN: self._handle_unknown_
        }[self.location]
        logger.debug(f'running step: {str(step)}')
        step()

    def _wait_(self, seconds: int = 1):
        logger.debug(f'sleeping for: {seconds}s')
        time.sleep(seconds)

    ###########################################################################
    # endregion
    #
    # region    LOCATION
    ###########################################################################

    @property
    def location(self):
        _location = Location.UNKNOWN
        i = 1
        while i < 10:

            # dynamically increase seek time
            self.driver.implicitly_wait(i * 0.1 * self.browser.config.timeout_multiplier)

            # new window
            try:
                if self.driver.current_url == Element.NEW_WINDOW_URL:
                    _location = Location.NEW_WINDOW
                    break
            except: pass

            # parked off hours
            try:
                if self.driver.current_url == self.off_hours_url:
                    _location = Location.OFF_HOURS_SITE
                    break
            except: pass

            # teams app download prompt
            try:
                use_web_app = self.driver.find_element(By.CLASS_NAME, Element.USE_WEB_APP_CLASS_NAME)
                if use_web_app.is_displayed():
                    _location = Location.USE_WEB_APP_PROMPT
                    break
            except: pass

            # teams app loading
            try:
                if self.driver.current_url == 'https://teams.microsoft.com/_':
                    _location = Location.TEAMS_APP_LOADING
                    logger.info('teams is loading')
                    break
            except: pass

            # teams app
            try:
                if self.driver.current_url.split('/')[2] == 'teams.microsoft.com':
                    time.sleep(1)
                    if self.driver.current_url.split('/')[2] == 'teams.microsoft.com':
                        waffle = self.driver.find_element(By.ID, Element.TEAMS_APP_WAFFLE_ID)
                        if waffle.is_displayed():
                            _location = Location.TEAMS_APP
                        break
            except: pass

            # pick an account
            try:
                pick_an_account = self.driver.find_element(By.ID, Element.PICK_AN_ACCOUNT_INDICATOR_ID)
                if pick_an_account.is_displayed():
                    _location = Location.PICK_AN_ACCOUNT
                    break
            except: pass

            # stay signed in
            try:
                stay_signed_in = self.driver.find_element(By.NAME, Element.STAY_SIGNED_IN_CHECKBOX_NAME)
                if stay_signed_in.is_displayed():
                    _location = Location.STAY_SIGNED_IN
                    break
            except: pass

            # mfa resend request
            try:
                mfa_resend_request = self.driver.find_element(By.ID, Element.MFA_RESEND_REQUEST_ID)
                if mfa_resend_request.is_displayed():
                    _location =  Location.MFA_RESEND_REQUEST
                    break
            except: pass

            # mfa user prompt
            try:
                mfa_user_prompt = self.driver.find_element(By.ID, Element.MFA_MS_AUTH_APP_USER_PROMPT_ID)
                if mfa_user_prompt.is_displayed():
                    _location =  Location.MFA_USER_PROMPT
                    break
            except: pass

            # mfa options
            try:
                mfa_options = self.driver.find_element(By.ID, Element.MFA_OPTIONS_LIST_CONTAINER_ID)
                if mfa_options.is_displayed():
                    _location =  Location.MFA_OPTIONS
                    break
            except: pass

            # mfa
            try:
                mfa_box = self.driver.find_element(By.NAME, Element.MFA_BOX_NAME)
                if mfa_box.is_displayed():
                    _location =  Location.MFA
                    break
            except: pass

            # password
            try:
                password_box = self.driver.find_element(By.NAME, Element.PASSWORD_BOX_NAME)
                if password_box.is_displayed():
                    _location =  Location.PASSWORD
                    break
            except: pass

            # password alternative
            try:
                password_alt_button = self.driver.find_element(By.ID, Element.PASSWORD_ALT_SELECT_ID)
                if password_alt_button.is_displayed():
                    _location =  Location.PASSWORD_ALT
                    break
            except: pass

            # username
            try:
                username_box = self.driver.find_element(By.NAME, Element.USERNAME_BOX_NAME)
                if username_box.is_displayed():
                    _location =  Location.LOGIN
                    break
            except: pass

            # unknown
            i += 1

        # self.driver.implicitly_wait(self.browser.config.element_timeout * self.browser.config.timeout_multiplier)
        logger.debug(f'determined location: {_location}')

        return _location


    def _handle_unknown_(self):
        logger.info('handling the unknown (failing out)')
        self._fail_(error='unknown location')

    ###########################################################################
    # endregion
    #
    # region    ELEMENT HELPERS
    ###########################################################################

    def _fill_element_(self, text: str, element: WebElement=None, parent: WebElement=None, by: By=None, value: str=None) -> str:

        try:
            if not element and parent: element = parent.find_element(by, value)
            elif not element and not parent: element = self.driver.find_element(by, value)
            element.send_keys(text)
            return None
        except NoSuchElementException as e:
            return f'element not found: {e}'
        except Exception as e:
            return f'an error occurred: {e}'
    

    def _click_button_(self, element: WebElement=None, parent: WebElement=None, by: By=None, value: str=None, use_submit: bool=False) -> str:

        try:
            if not element and parent: element = parent.find_element(by, value)
            elif not element and not parent: element = self.driver.find_element(by, value)
            if use_submit:
                element.submit()
            else:
                element.click()
            return None
        except NoSuchElementException as e:
            return f'element not found: {e}'
        except Exception as e:
            return f'an error occurred: {e}'
    
    ###########################################################################
    # endregion
    #
    # region    LOGIN
    ###########################################################################

    def _load_website_(self):
        logger.info('loading website')

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
        try:
            self.driver.get(url)
            logger.debug('website loaded')
        except Exception as e:
            self._fail_(error=f'failed to load Teams: {e}')


    def _submit_username_(self):
        logger.debug('entering username')
        error = self._fill_element_(text=self.browser.config.username, by=By.NAME, value=Element.USERNAME_BOX_NAME)
        if error: 
            self._fail_(error=error)
            return

        logger.info('submitting username')
        submit = [e for e in self.driver.find_elements(By.TAG_NAME, 'input') if e.get_attribute('value') == Element.USERNAME_NEXT_BUTTON_VALUE][0]
        error = self._click_button_(element=submit)
        if error: 
            self._fail_(error=error)
            return

        try: WebDriverWait(self.driver, self.browser.config.element_timeout).until_not(EC.element_to_be_clickable((By.NAME, Element.USERNAME_BOX_NAME)))
        except StaleElementReferenceException as e: pass
        
        logger.debug('username submitted')


    def _submit_password_(self):
        logger.debug('entering password')
        error = self._fill_element_(text=crypto.decryptWithKeyFromBase64(base64key=self.browser.config.key, base64data=self.browser.config.password), by=By.NAME, value=Element.PASSWORD_BOX_NAME)
        if error: 
            self._fail_(error=error)
            return

        logger.info('submitting password')
        submit = [e for e in self.driver.find_elements(By.TAG_NAME, 'input') if e.get_attribute('value') == Element.PASSWORD_SUBMIT_BUTTON_VALUE][0]
        error = self._click_button_(element=submit)
        if error: 
            self._fail_(error=error)
            return
        
        try: WebDriverWait(self.driver, self.browser.config.element_timeout).until_not(EC.element_to_be_clickable((By.NAME, Element.PASSWORD_BOX_NAME)))
        except StaleElementReferenceException as e: pass
        
        logger.debug('password submitted')


    def _handle_password_alt_(self):
        logger.debug('using password alternative')
        
        # determine alternative method
        method = None
        method_info = None
        try:
            auth_app_prompt = self.driver.find_element(By.ID, Element.MFA_PROMPT_INSTEAD_PASSWORD_ID)
            if auth_app_prompt.is_displayed():
                method = 'auth_app'
                method_info = auth_app_prompt.text
        except: pass

        if not method or not method_info:
            self._fail_(error='unhandled alternative password method')
            return


        # send auth app login
        if 'auth_app' == method:
            try:
                error = self._notify_user_(msg=f'{APP_NAME} - MFA Number - {method_info}', level=logging.CRITICAL, force=True)
                logger.info(f'user prompted for MFA response: {method_info}')
                if error:
                    self._fail_(error=error)
                    return

                try: WebDriverWait(self.driver, 60).until_not(EC.element_to_be_clickable((By.ID, Element.MFA_PROMPT_INSTEAD_PASSWORD_ID)))
                except StaleElementReferenceException as e: pass

                try: 
                    if self.driver.find_element(By.ID, Element.PASSWORD_ALT_SELECT_ID):
                        error = self._click_button_(by=By.ID, value=Element.MFA_PROMPT_INSTEAD_PASSWORD_RESEND_ID)
                        if error:
                            self._fail_(error=f'failed to resend password alternative mfa prompt: {error}')
                            return

                        self._fail_(error='auth app password alternative request timed out')
                        return
                except: pass
            except Exception as error:
                self._fail_(error=error)
                return
            
        logger.debug('logged in using password alternative')


    def _stay_signed_in_(self):
        logger.info('staying signed in')
        yes = [e for e in self.driver.find_elements(By.TAG_NAME, 'input') if e.get_attribute('value') == 'Yes'][0]
        error = self._click_button_(element=yes)
        if error:
            self._fail_(error=error)
            return

        try: WebDriverWait(self.driver, self.browser.config.element_timeout).until_not(EC.element_to_be_clickable(yes))
        except StaleElementReferenceException as e: pass
        
        logger.debug('signed in')
        
    
    def _pick_an_account_(self):
        logger.info('selecting account')
        account = [e for e in self.driver.find_elements(By.CLASS_NAME, Element.PICK_AN_ACCOUNT_LIST_CLASS_NAME) if e.get_attribute(Element.PICK_AN_ACCOUNT_LIST_ITEM_ATTRIBUTE) == self.browser.config.username][0]
        error = self._click_button_(element=account)
        if error:
            self._fail_(error=error)
            return

        try: WebDriverWait(self.driver, self.browser.config.element_timeout).until_not(EC.element_to_be_clickable(account))
        except StaleElementReferenceException as e: pass
        
        logger.debug('account selected')

    ###########################################################################
    # endregion
    #
    # region    MFA
    ###########################################################################

    def _handle_mfa_(self):
        logger.info('handling MFA')

        if self.browser.config.force_auth_app_notification:
            error = self._force_auth_app_()
            if error:
                self._fail_(error=error)
                return
            return
        
        mfa_type = 'unknown'

        # one time code entry
        try:
            mfa_type_id = self.driver.find_element(By.NAME, 'otc').get_attribute('id')
            if mfa_type_id == Element.MFA_BY_CODE_ID:
                error = self._enter_mfa_otc_()
                if error:
                    self._fail_(error=error)
                    return
                logger.info('MFA handled')
                return
        except:
            pass

        # number
        try:
            if Element.MFA_MS_AUTH_APP_ENTER_NUMBER_DESCRIPTION_TEXT == self.driver.find_element(By.ID, Element.MFA_MS_AUTH_APP_USER_PROMPT_ID).text:
                self._prompt_user_()
        except:
            pass

    
    def _force_auth_app_(self):
        logger.debug('forcing auth app')

        error = self._click_button_(by=By.ID, value=Element.MFA_SIGN_IN_ANOTHER_WAY_ID)
        if error: return error

        try: WebDriverWait(self.driver, self.browser.config.element_timeout).until_not(EC.element_to_be_clickable((By.ID, Element.MFA_SIGN_IN_ANOTHER_WAY_ID)))
        except StaleElementReferenceException as e: pass
        
        logger.debug('clicked for other options')


    def _select_mfa_option_(self):
        mfa_option = Element.MFA_MS_AUTH_APP_OPTION_ID if self.browser.config.force_auth_app_notification else 'Unknown'
        logger.debug(f'selecting mfa option: {mfa_option}')

        options = self.driver.find_element(By.ID, Element.MFA_OPTIONS_LIST_CONTAINER_ID).find_elements(By.CLASS_NAME, Element.MFA_OPTION_BUTTON_CLASS)
        button = [e for e in options if e.get_attribute(Element.MFA_OPTION_BUTTON_ATTRIBUTE) == mfa_option][0]
        error = self._click_button_(element=button)
        if error:
            self._fail_(error=error)
            return

        try: WebDriverWait(self.driver, self.browser.config.element_timeout).until_not(EC.element_to_be_clickable(button))
        except StaleElementReferenceException as e: pass
        
        logger.debug(f'selected mfa option: {mfa_option}')


    def _prompt_user_(self):
        logger.debug('sending prompt to user')

        prompt_type: str = None
        try:
            prompt_type = {
                Element.MFA_MS_AUTH_APP_ENTER_NUMBER_DESCRIPTION_TEXT: 'number'
            }[self.driver.find_element(By.ID, Element.MFA_MS_AUTH_APP_USER_PROMPT_ID).text]
        except Exception as error:
            self._fail_(error=error)
            return

        if 'number' == prompt_type:
            try:
                number = self.driver.find_element(By.ID, Element.MFA_MS_AUTH_APP_ENTER_NUMBER_ID).text
                error = self._notify_user_(msg=f'{APP_NAME} - MFA Number - {number}', level=logging.CRITICAL, force=True)
                logger.info(f'user prompted for MFA response ({number})')
                if error:
                    self._fail_(error=error)
                    return

                try: WebDriverWait(self.driver, 60).until_not(EC.element_to_be_clickable((By.ID, Element.MFA_MS_AUTH_APP_ENTER_NUMBER_ID)))
                except StaleElementReferenceException as e: pass

                try: 
                    if self.driver.find_element(By.ID, Element.MFA_RESEND_REQUEST_ID):
                        self._fail_(error='request timed out')
                        return
                except:
                    pass
                
            except Exception as error:
                self._fail_(error=error)
                return
        

    def _mfa_resend_request_(self):
        logger.info('resending MFA request')

        error = self._click_button_(by=By.ID, value=Element.MFA_RESEND_REQUEST_ID)
        if error:
            self._fail_(error=error)
            return

        logger.debug('resent MFA request')


    def _enter_mfa_otc_(self):
        logger.info('requesting MFA code')
        code = input('\n\nOTC Code: ')

        if not code:
            self._fail_(error='MFA code not provided')
            return

        logger.info('entering MFA code')
        error = self._fill_element_(text=code, by=By.NAME, value='otc')
        if error: 
            self._fail_(error=error)
            return

        logger.info('submitting MFA code')
        verify = [e for e in self.driver.find_elements(By.TAG_NAME, 'input') if e.get_attribute('value') == Element.MFA_SUBMIT_BUTTON_VALUE][0]
        error = self._click_button_(element=verify)
        if error: 
            self._fail_(error=error)
            return

        try: WebDriverWait(self.driver, self.browser.config.element_timeout).until_not(EC.element_to_be_clickable(verify))
        except StaleElementReferenceException as e: pass
        
        logger.info('MFA code submitted')
    
    ###########################################################################
    # endregion
    #
    # region    TEAMS
    ###########################################################################

    def _handle_use_web_app_prompt_(self): 
        logger.debug('selecting web app (bypass app download)')
        error = self._click_button_(by=By.CLASS_NAME, value=Element.USE_WEB_APP_CLASS_NAME)
        if error:
            self._fail_(error=error)
        logger.debug('web app selected (app download bypassed)')

    def _wait_for_teams_load_(self):
        while self.location == Location.TEAMS_APP_LOADING:
            self._wait_(seconds=5 * self.browser.config.timeout_multiplier)
        try: 
            if self.driver.current_url.split('/')[2] == 'teams.microsoft.com':
                logger.info('teams app loaded')
        except: pass

    def _handle_teams_(self):

        should_be_logged_in = self.teams.should_be_logged_in
        parked = self.location == Location.OFF_HOURS_SITE

        # if we should be logged in and are parked
        if parked and should_be_logged_in:
            self._load_website_()

        # if we should be logged in and aren't parked
        if not parked and should_be_logged_in:

            # if new window then load website, else be active
            if self.location == Location.NEW_WINDOW:
                self._load_website_()
            else:
                self._be_active_()

        # if we shouldn't be logged in and are already parked
        if parked and not should_be_logged_in:
            self._handle_off_hours_()

        # if we shouldn't be logged in and aren't already parked
        if not parked and not should_be_logged_in:
            self._go_off_hours_()

    def _be_active_(self):
        logger.debug('being active')

        if self.teams.last_action == 'clicked_teams':
            self._click_chat_()
        elif self.teams.last_action == 'clicked_chat':
            self._click_teams_()
        else:
            self._click_chat_()

        try:
            desired_availability, desired_start, desired_end = self.teams.desired_availability
            if self._get_current_status_() != desired_availability:
                if self.teams.schedule.randomStatusModifierLimit:
                    now = datetime.datetime.now()
                    max_desired_start = desired_start.__add__(datetime.timedelta(minutes=self.teams.schedule.randomStatusModifierLimit))
                    rnd_mins = int(round((max_desired_start - now).total_seconds() / 60, 0))
                    rnd_mins = rnd_mins if rnd_mins >= 0 else 0
                    rnd_desired_start = self.teams.schedule._gen_rnd_mod_(limit=rnd_mins, t=desired_start)
                    if max_desired_start >= desired_end or rnd_desired_start < datetime.datetime.now():
                        error = self._set_status_(status=desired_availability)
                
                else:
                    error = self._set_status_(status=desired_availability)

                if error:
                    self._fail_(error=error)
                    return
        except Exception as error:
            print(error)

        logger.debug('resting')
        self._wait_(seconds=self.browser.config.teams_activity_interval)
        logger.debug('resuming')

        return
    
    @property
    def _profile_name_(self) -> str:
        if not self.teams.profile_name:
            logger.debug('getting profile name')
            error = self._access_profile_()
            if error: return None
            try:
                self.teams.profile_name = self.driver.find_element(By.CLASS_NAME, Element.TEAMS_USER_PROFILE_NAME_CLASS_NAME).find_element(By.TAG_NAME, 'span').text
                logger.debug(f'profile name: {self.teams.profile_name}')
            except Exception as error:
                logger.error(f'failed to retrive profile name: {error}')
                return None

        self._close_profile_dropdown_()
        return self.teams.profile_name

    def _click_me_(self):
        logger.debug('clicking self')

        pinned_chats = self.driver.find_element(By.XPATH, Element.CHAT_PINNED_LIST_FROM_CHAT_TAB_XPATH).find_elements(By.TAG_NAME, 'div')
        for user in pinned_chats:
            if '(You)' in user.text:
                button = user.find_element(By.TAG_NAME, 'a')
                error = self._click_button_(element=button)
                if error: logger.error(error)
                else: logger.debug('clicked self')
                return error
    
    def _click_chat_(self):
        logger.debug('clicking chat')
        chat = [e for e in self.driver.find_elements(By.CLASS_NAME, Element.APP_BUTTON_LABEL_CLASS_NAME) if e.text == Element.CHAT_BUTTON_LABEL_TEXT][0].find_element(By.XPATH, './..')
        error = self._click_button_(element=chat)
        if error:
            self._fail_(error=error)
            return
        self.teams.last_action = 'clicked_chat'

        self._click_me_()

        logger.debug('chat clicked')

    def _click_teams_(self):
        logger.debug('clicking teams')
        teams = [e for e in self.driver.find_elements(By.CLASS_NAME, Element.APP_BUTTON_LABEL_CLASS_NAME) if e.text == Element.TEAMS_BUTTON_LABEL_TEXT][0].find_element(By.XPATH, './..')
        error = self._click_button_(element=teams)
        if error:
            self._fail_(error=error)
            return
        self.teams.last_action = 'clicked_teams'
        logger.debug('clicked teams')

    def _access_profile_(self) -> str:
        try:
            self.driver.find_element(By.ID, Element.TEAMS_STATUS_TEXT_ID)
            return None
        except:
            logger.debug('accessing profile')
            return self._click_button_(by=By.ID, value=Element.TEAMS_PERSONAL_DROPDOWN_ID)

    def _close_profile_dropdown_(self) -> str:
        try:
            self.driver.find_element(By.ID, Element.TEAMS_STATUS_TEXT_ID)
            return self._click_button_(by=By.ID, value=Element.TEAMS_PERSONAL_DROPDOWN_ID)
        except:
            return None

    def _get_current_status_(self) -> str:
        logger.debug('getting current status')
        error = self._access_profile_()
        if error:
            logger.error(error)
        
        try:
            status_text = self.driver.find_element(By.ID, Element.TEAMS_STATUS_TEXT_ID).text
            status = Teams.convert_availability_name_to_enum(value=status_text)
            self.teams.current_availability = status
        except Exception as error:
            logger.error(error)
            logger.debug(f'setting status to {Availability.UNKNOWN.value}')
            self.teams.current_availability = Availability.UNKNOWN


        if self.teams.initial_availability == Availability.UNKNOWN:
            self.teams.initial_availability = status
            self._notify_user_(msg=f'Initial Status: {status_text} | Resolved Status: {status.value}', level=logging.INFO)

        logger.debug(f'Current Status: {status_text} | Resolved Status: {status.value}')
        self._notify_user_(msg=f'Current Status: {status_text} | Resolved Status: {status.value}', level=logging.DEBUG)

        self._close_profile_dropdown_()
        logger.debug('current status obtained')
        
        return status

    def _set_status_(self, status: Availability) -> str:
        logger.info(f'setting status to: {status.value}')
        self._access_profile_()

        error = self._click_button_(by=By.ID, value=Element.TEAMS_USER_PRESENCE_BUTTON_ID)
        if error:
            return error
        
        try:
            buttons = self.driver.find_element(By.CLASS_NAME, 'settings-presence-popover').find_elements(By.TAG_NAME, 'li')
            for b in buttons:
                resolved_button_status = {
                    'Available': Availability.AVAILABLE,
                    'Busy': Availability.BUSY,
                    'Do not disturb': Availability.DND,
                    'Appear away': Availability.AWAY,
                    'Appear offline': Availability.OFFLINE,
                    'Be right back': None,
                    'Duration': None,
                    'Reset status': None,
                    None: None
                }[b.get_attribute('aria-label')]
                if resolved_button_status == status:
                    button = b.find_element(By.TAG_NAME, 'button')

            error = self._click_button_(element=button)
            if error:
                self._fail_(error=error)
                return

            self._close_profile_dropdown_()
        except Exception as error:
            self._fail_(error=error)
            return

        self._notify_user_(msg=f'Set Status: {status.value}', level=logging.INFO)

    def _logout_(self):
        logger.debug('logging out')
        error = self._access_profile_()
        if error:
            self._fail_(error=error)
            return
        
        error = self._click_button_(by=By.ID, value=Element.TEAMS_LOGOUT_BUTTON_ID)
        if error:
            self._fail_(error=error)
            return
        
        try: WebDriverWait(self.driver, self.browser.config.element_timeout).until_not(EC.element_to_be_clickable((By.ID, Element.TEAMS_LOGOUT_BUTTON_ID)))
        except StaleElementReferenceException as e: pass

        logger.debug('confirming logout')
        error = self._click_button_(by=By.ID, value=Element.TEAMS_LOGOUT_CONFIRM_ID)
        if error:
            self._fail_(error=error)
            return
        
        try: WebDriverWait(self.driver, self.browser.config.element_timeout).until_not(EC.element_to_be_clickable((By.ID, Element.TEAMS_LOGOUT_CONFIRM_ID)))
        except StaleElementReferenceException as e: pass

        logger.info('logged out')

    def _go_off_hours_(self):
        logger.debug('going off hours')

        self._set_status_(status=Availability.OFFLINE)

        logger.debug('stopping activity')

        try:
            self.driver.get(self.off_hours_url)
            logger.debug(f'{self.off_hours_url} loaded')
        except Exception as e:
            self._fail_(error=f'failed to load {self.off_hours_url}: {e}')

        logger.info('activity stopped... for now')

    def _handle_off_hours_(self):
        now = datetime.datetime.now()
        
        # time until login
        login = self.teams.next_login_datetime(now=now)
        seconds = (login-now).total_seconds()

        # don't sleep for zero seconds plz
        if 0 == seconds: return

        # readable login
        readable_login_datetime = "%d:%02d:%02d" % (login.hour, login.minute, login.second)

        # readable time until login
        hours = seconds/60/60
        readable_time_until_login = "%d:%02d:%02d" % (int(hours), (hours*60) % 60, (hours*3600) % 60)

        logger.info(f'sleeping for {readable_time_until_login} ({str(calendar.day_name[login.weekday()])[:3]} {readable_login_datetime})')
        self._notify_user_(msg=f'sleeping for {readable_time_until_login} ({str(calendar.day_name[login.weekday()])[:3]} {readable_login_datetime})', level=logging.INFO)
        self._wait_(seconds=int(seconds))
        logger.info(f'waking up')
        self._notify_user_(msg='waking up', level=logging.INFO)

    ###########################################################################
    # endregion
    pass
