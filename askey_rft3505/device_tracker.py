"""Support for Askey RFT3505 Router (Movistar Spain)"""
import base64
from datetime import datetime
import hashlib
import logging
import re
import requests
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.device_tracker import (DOMAIN, PLATFORM_SCHEMA, DeviceScanner)
from homeassistant.const import (CONF_HOST, CONF_PASSWORD, HTTP_HEADER_X_REQUESTED_WITH)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PASSWORD): cv.string
})

def get_scanner(hass, config):
    """Validate the configuration and return a scanner."""

    scanner = AskeyDeviceScanner(config[DOMAIN])
    return scanner if scanner.success_init else None


class AskeyDeviceScanner(DeviceScanner):
    """This class queries a Askey RFT3505 Fiber Router (Movistar Spain)"""

    def __init__(self, config):
        """Initialize the scanner."""
        self.host = config[CONF_HOST]
        self.password = config[CONF_PASSWORD]

        self.parse_macs = re.compile(r'([0-9a-fA-F]{2}:' + '[0-9a-fA-F]{2}:' + '[0-9a-fA-F]{2}:' + '[0-9a-fA-F]{2}:' + '[0-9a-fA-F]{2}:' + '[0-9a-fA-F]{2})')
        self.parse_device_data = re.compile(r'var deviceData=([\w\W]+?);')

        self.login_url = 'http://{ip}/te_acceso_router.cgi'.format(**{'ip': self.host})

        self.last_results = {}
        self.success_init = self._update_info()

    def scan_devices(self):
        """Scan for new devices and return a list with found device IDs."""
        self._update_info()
        return self.last_results

    def get_device_name(self, device):
        """This router doesn't save the name of the wireless device."""
        return None

    def _update_info(self):
        """Ensure the information from the router is up to date.
        Return boolean if scanning successful.
        """
        _LOGGER.info('Checking Router')

        data = self.get_askey_info()
        if not data:
            return False

        self.last_results = data
        return True

    def get_askey_info(self):
        """Retrieve data from router."""

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0',
                   'Cookie': 'sessionID=123456789'}
        data = {'loginPassword': self.password}

        session = requests.Session()
        login_response = session.post(self.login_url, data=data, headers=headers)
        result = list()
        if login_response.status_code == 200:
            url = 'http://{}/te_mapa_red_local.html'.format(self.host)
            response = session.get(url, headers=headers, timeout=4)
            response_string = str(response.content)
            for line in response_string.split("\n"):
                if "deviceData" in line:
                    line_replaced = line.replace("\\", "")
                    devices_data = eval(self.parse_device_data.search(line_replaced).group(1))
                    break
            for device in devices_data:
                if device[0] == '1':
                    result.append(device[6])
        else:
            result = None
            _LOGGER.info('Error connecting to the router...')

        session.close()
        return result
