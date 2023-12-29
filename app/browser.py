import json
from app.config import Config, Config_Options
from app.lumberjack import Lumberjack
from enum import Enum
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER as gecko_logger
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


logger: Lumberjack

class Browser:

    class Status(Enum):
        CLOSED: str = 'closed'
        OPEN: str = 'open'
        PENDING: str = 'pending'

    ###########################################################################
    # region    DEFAULT CONSTRUCTOR
    ###########################################################################

    config: Config_Options
    browser_options: webdriver.ChromeOptions
    driver: webdriver.Chrome
    open_count: int = 0
    initial_url: str = ''

    def __init__(self, initial_url: str='', config: Config_Options=None, browser_options: webdriver.ChromeOptions=None) -> None:
        
        # logging
        global logger
        logger = Lumberjack(__file__, console_output=config.console_output)

        self.initial_url = initial_url
        self.config: Config_Options = config if config else Config_Options()
    
    ###########################################################################
    # endregion
    #
    # region    LOGGING/TRACKING
    ###########################################################################

    @property
    def status(self):
        try:
            if bool(self.driver.current_url):
                return Browser.Status.OPEN
            else:
                return Browser.Status.PENDING
        except:
            return Browser.Status.CLOSED

    ###########################################################################
    # endregion
    #
    # region    OPEN BROWSER
    ###########################################################################

    def open(self):

        # set browser options
        logger.debug('initializing browser')
        self.browser_options = webdriver.ChromeOptions()
        if not self.config.interactive:
            self.browser_options.headless = True
            self.browser_options.add_argument('--disable-notifications')
            self.browser_options.add_argument('disable-infobars')

            # for docker:
            self.browser_options.add_argument('--no-sandbox')
            self.browser_options.add_argument('--disable-dev-shm-usage')
            assert self.browser_options.headless
        if self.config.open_dev_tools:
            self.browser_options.add_argument('--auto-open-devtools-for-tabs')

        gecko_logger.setLevel(self.config.gecko_log_level)

        # initialize driver
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(
            service=service,
            options=self.browser_options
        )
        
        # input('Position browser to desired location then press any key...')
        # rect = self.driver.get_window_rect()
        # self.config.browser_height = rect['height']
        # self.config.browser_width = rect['width']
        # self.config.browser_pos_x = rect['x']
        # self.config.browser_pos_y = rect['y']
        # print(f'Updated config to the following: {rect}')
        # Config._update_config_file_(config_options=self.config)

        # post-init settings
        self.driver.set_window_rect(x=self.config.browser_pos_x,
                                    y=self.config.browser_pos_y,
                                    width=self.config.browser_width,
                                    height=self.config.browser_height)
        self.driver.implicitly_wait(self.config.element_timeout * self.config.timeout_multiplier)

        logger.info(f"Browser Initialized - {'Interactive' if self.config.interactive else 'Headless'} - {self.config.browser_width}x{self.config.browser_height}")
        logger.info(f'ID: {self.driver.session_id}')

        if self.initial_url:
            self.driver.get(self.initial_url)

        return self.status

    ###########################################################################
    # endregion
    #
    # region    CLOSE BROWSER
    ###########################################################################

    def close(self):
        if self.status == Browser.Status.OPEN:
            self.driver.close()
            logger.info(f"Browser Closed - ID: {self.driver.session_id}")

    def handle_browser_not_found(self):
        self.close()
        self.open()


    ###########################################################################
    # endregion
    #
    # region    EXIT
    ###########################################################################

    def exit(self, exit_reason='connection closed'):
        self.close()
        self.driver.__exit__(None, None, None)
        logger.info(exit_reason)

    ###########################################################################
    # endregion
    ###########################################################################
