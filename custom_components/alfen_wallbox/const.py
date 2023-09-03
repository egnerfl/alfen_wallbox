
DOMAIN = "alfen_wallbox"

KEY_MAC = "mac"
KEY_IP = "ip"

TIMEOUT = 60

SERVICE_REBOOT_WALLBOX = "reboot_wallbox"
SERVICE_SET_CURRENT_LIMIT = "set_current_limit"
SERVICE_ENABLE_RFID_AUTHORIZATION_MODE = "enable_rfid_authorization_mode"
SERVICE_DISABLE_RFID_AUTHORIZATION_MODE = "disable_rfid_authorization_mode"

ALFEN_PRODUCT_MAP = {
    'NG910-60123': 'Eve Single Pro-Line DE, 3 phase, display, type 2 socket',
    'NG910-60127': 'Eve Single Pro-Line DE, 3 phase, display, charging cable',
    
    'NG900-60503': 'Eve Single S-line, 1 phase, LED, type 2 socket',
    'NG900-60505': 'Eve Single S-line, 1 phase, LED, type 2 shutter',
    'NG900-60507': 'Eve Single S-line, 1 phase, LED, charging cable',
    'NG910-60587': 'Eve Single S-line, 3 phase, LED, charging cable',
    'NG910-60583': 'Eve Single Pro-line, 3 phase, LED, type 2 socket',
    'NG910-60003': 'Eve Single Pro-line, 1 phase, display, type 2 socket',
    'NG910-60005': 'Eve Single Pro-line, 1 phase, display, type 2 shutter',
    'NG910-60007': 'Eve Single Pro-line, 1 phase, display, charging cable',
    'NG910-60023': 'Eve Single Pro-line, 3 phase, display, type 2 socket',
    'NG910-60025': 'Eve Single Pro-line, 3 phase, display, type 2 shutter',
    'NG910-60027': 'Eve Single Pro-line, 3 phase, display, charging cable',

    'NG920-61031': 'Eve Double Pro-line, 2 x type 2 socket, 1 phase, max. 1x32A input current',
    'NG920-61032': 'Eve Double Pro-line, 2 x type 2 socket, 2 phase, max. 1x32A input current',
    'NG920-61021': 'Eve Double Pro-line, 2 x type 2 socket, 3 phase, max. 1x32A input current',
    'NG920-61022': 'Eve Double Pro-line, 2 x type 2 socket, 3 phase, max. 2x32A input current',

    'Generic Alfen Wallbox': 'Generic Alfen Wallbox',
}
