from dataclasses import dataclass
from enum import Enum

class Location(Enum):
    UNKNOWN = 'unknown'
    NEW_WINDOW = 'new_window'
    LOGIN = 'login'
    PASSWORD = 'password'
    PASSWORD_ALT = 'password_alt'
    MFA = 'mfa'
    MFA_OPTIONS = 'mfa_options'
    MFA_USER_PROMPT = 'mfa_user_prompt'
    MFA_RESEND_REQUEST = 'mfa_resend_request'
    STAY_SIGNED_IN = 'stay_signed_in'
    PICK_AN_ACCOUNT = 'pick_an_account'
    USE_WEB_APP_PROMPT = 'use_web_app_prompt'
    TEAMS_APP_LOADING = 'teams_app_loading'
    TEAMS_APP = 'teams_app'
    OFF_HOURS_SITE = 'off_hours_site'

@dataclass
class Element():
    NEW_WINDOW_URL: str = 'data:,'
    USERNAME_BOX_NAME: str = 'loginfmt'
    USERNAME_NEXT_BUTTON_VALUE: str = 'Next'
    PASSWORD_BOX_NAME: str = 'passwd'
    PASSWORD_SUBMIT_BUTTON_VALUE: str = 'Sign in'

    PASSWORD_ALT_SELECT_ID: str = 'idA_PWD_SwitchToCredPicker'
    MFA_PROMPT_INSTEAD_PASSWORD_ID: str = 'idRemoteNGC_DisplaySign'
    MFA_PROMPT_INSTEAD_PASSWORD_RESEND_ID: str = 'idSIButton9'

    MFA_SIGN_IN_ANOTHER_WAY_ID: str = 'signInAnotherWay'
    MFA_OPTIONS_LIST_CONTAINER_ID: str = 'idDiv_SAOTCS_Proofs'
    MFA_OPTION_BUTTON_CLASS: str = 'table'
    MFA_OPTION_BUTTON_ATTRIBUTE: str = 'data-value'

    MFA_APPROVE_SIGN_IN_TITLE_ID: str = 'idDiv_SAOTCAS_Title'
    MFA_APPROVE_SIGN_IN_TITLE_TEXT: str = 'Approve sign in request'

    MFA_MS_AUTH_APP_OPTION_ID: str = 'PhoneAppNotification'

    MFA_MS_AUTH_APP_USER_PROMPT_ID: str = 'idDiv_SAOTCAS_Description'
    MFA_MS_AUTH_APP_ENTER_NUMBER_DESCRIPTION_TEXT: str = 'Open your Authenticator app, and enter the number shown to sign in.'    
    MFA_MS_AUTH_APP_ENTER_NUMBER_ID: str = 'idRichContext_DisplaySign'
    
    MFA_RESEND_REQUEST_ID: str = 'idA_SAASTO_Resend'

    MFA_BOX_NAME: str = 'otc'
    MFA_BY_CODE_ID: str = 'idTxtBx_SAOTCC_OTC'
    MFA_SUBMIT_BUTTON_VALUE: str = 'Verify'

    STAY_SIGNED_IN_CHECKBOX_NAME: str = 'DontShowAgain'
    PICK_AN_ACCOUNT_INDICATOR_ID: str = 'otherTile'
    PICK_AN_ACCOUNT_LIST_CLASS_NAME: str = 'table'
    PICK_AN_ACCOUNT_LIST_ITEM_ATTRIBUTE: str = 'data-test-id'

    USE_WEB_APP_CLASS_NAME: str = 'use-app-lnk'

    TEAMS_APP_WAFFLE_ID: str = 'ts-waffle-button'
    APP_BUTTON_CLASS_NAME: str = 'app-bar-button'
    APP_BUTTON_LABEL_CLASS_NAME: str = 'app-bar-text'
    CHAT_BUTTON_LABEL_TEXT: str = 'Chat'
    TEAMS_BUTTON_LABEL_TEXT: str = 'Teams'
    TEAMS_STATUS_TEXT_ID: str = 'personal-skype-status-text'
    TEAMS_PERSONAL_DROPDOWN_ID: str = 'personDropdown'
    TEAMS_USER_PRESENCE_BUTTON_ID: str = 'settings-dropdown-user-presence-button'
    TEAMS_USER_PROFILE_NAME_CLASS_NAME: str = 'profile-name-text'

    CHAT_TAB_ID: str = 'chatstab'
    CHAT_PINNED_LIST_FROM_CHAT_TAB_XPATH: str = '//*[@id="chatstab"]/div/div/chat-list-bridge/div/div[1]/div/ul/li[1]/div[2]'
    NEW_CHAT_XPATH: str = '/html/body/div[2]/div[2]/div[1]/div/left-rail/div/div/left-rail-chat-tabs/div/left-rail-header/div/div[2]/button[2]'
    NEW_CHAT_RECIP_SEARCH_ID: str = 'people-picker-input'
    CHAT_MESSAGE_BOX_XPATH: str = '/html/body/div[1]/div/div/div/div/div[6]/div/div/div[2]/div/div[4]/div[1]/div[3]/div/p'
    SEND_MESSAGE_BUTTON_NAME: str = 'send'

    TEAMS_LOGOUT_BUTTON_ID: str = 'logout-button'
    TEAMS_LOGOUT_CONFIRM_ID: str = 'confirmButton'

class Availability(Enum):
    AVAILABLE = 'Available'
    BUSY = 'Busy'
    DND = 'DoNotDisturb'
    AWAY = 'Away'
    OFFLINE = 'Offline'
    UNKNOWN = 'Unknown'
    
class Activity(Enum):
    AVAILABLE = 'Available'
    OFF_WORK = 'OffWork'
    UNKNOWN = 'Unknown'
