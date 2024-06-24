import logging

import requests
import time
import ssl
from enum import Enum
from datetime import timedelta

from homeassistant.util import Throttle
from .const import DOMAIN, ALFEN_PRODUCT_MAP

HEADER_JSON = {"content-type": "alfen/json; charset=utf-8"}
POST_HEADER_JSON = {"content-type": "application/json"}

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)


class AlfenDevice:
    def __init__(self, host, name, session, username, password):
        self.host = host
        self.name = name
        self._status = None
        self._session = session
        self.username = username
        if self.username is None:
            self.username = "admin"
        self.password = password
        # Default ciphers needed as of python 3.10
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.ssl = context

    async def init(self):
        await self.async_get_info()
        self.id = "alfen_{}".format(self.info.identity)
        if self.name is None:
            self.name = f"{self.info.identity} ({self.host})"
        await self.async_update()

    @property
    def status(self):
        return self._status

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return {
            "identifiers": {(DOMAIN, self.id)},
            "manufacturer": "Alfen",
            "model": self.info.model,
            "name": self.name,
            "sw_version": self.info.firmware_version,
        }

    def _request(self, parameter_list):
        pass

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        await self._do_update()

    async def _do_update(self):
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )
        response = await self._session.request(
            ssl=self.ssl,
            method="GET",
            headers=HEADER_JSON,
            url=self.__get_url(
                "prop?ids=2060_0,2056_0,2221_3,2221_4,2221_5,2221_A,2221_B,2221_C,2221_16,2201_0,2501_2,2221_22,2129_0,2126_0"
            ),
        )

        _LOGGER.debug(f"Status Response {response}")
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )
        response_json = await response.json(content_type=None)
        _LOGGER.debug(response_json)

        self._status = AlfenStatus(response_json, self._status)

    async def async_get_info(self):
        response = await self._session.request(
            ssl=self.ssl, method="GET", url=self.__get_url("info")
        )
        _LOGGER.debug(f"Response {response}")

        if response.status != 200:
            _LOGGER.debug("Info API not available, use generic info")

            generic_info = {
                "Identity": self.host,
                "FWVersion": "?",
                "Model": "Generic Alfen Wallbox",
                "ObjectId": "?",
                "Type": "?",
            }
            self.info = AlfenDeviceInfo(generic_info)
        else:
            response_json = await response.json(content_type=None)
            _LOGGER.debug(response_json)

            self.info = AlfenDeviceInfo(response_json)

    async def reboot_wallbox(self):
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("cmd"),
            json={"command": "reboot"},
        )
        _LOGGER.debug(f"Reboot response {response}")
        self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )

    async def set_current_limit(self, limit):
        _LOGGER.debug(f"Set current limit {limit}A")
        if limit > 32 | limit < 1:
            return self.async_abort(reason="invalid_current_limit")

        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("prop"),
            json={"2129_0": {"id": "2129_0", "value": limit}},
        )
        _LOGGER.debug(f"Set current limit response {response}")
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )
        await self._do_update()

    async def set_rfid_auth_mode(self, enabled):
        _LOGGER.debug(f"Set RFID Auth Mode {enabled}A")

        value = 0
        if enabled:
            value = 2

        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("prop"),
            json={"2126_0": {"id": "2126_0", "value": value}},
        )
        _LOGGER.debug(f"Set RFID Auth Mode {response}")
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )
        await self._do_update()

    def __get_url(self, action):
        return "https://{}/api/{}".format(self.host, action)


class AlfenStatus:
    def __init__(self, response, prev_status):
        for prop in response["properties"]:
            _LOGGER.debug("Prop")
            _LOGGER.debug(prop)

            if prop["id"] == "2060_0":
                self.uptime = max(0, prop["value"] / 1000 * 60)
            elif prop["id"] == "2056_0":
                self.bootups = prop["value"]
            elif prop["id"] == "2221_3":
                self.voltage_l1 = round(prop["value"], 2)
            elif prop["id"] == "2221_4":
                self.voltage_l2 = round(prop["value"], 2)
            elif prop["id"] == "2221_5":
                self.voltage_l3 = round(prop["value"], 2)
            elif prop["id"] == "2221_A":
                self.current_l1 = round(prop["value"], 2)
            elif prop["id"] == "2221_B":
                self.current_l2 = round(prop["value"], 2)
            elif prop["id"] == "2221_C":
                self.current_l3 = round(prop["value"], 2)
            elif prop["id"] == "2221_16":
                self.active_power_total = round(prop["value"], 2)
            elif prop["id"] == "2201_0":
                self.temperature = round(prop["value"], 2)
            elif prop["id"] == "2501_2":
                self.status = prop["value"]
            elif prop["id"] == "2221_22":
                self.meter_reading = round((prop["value"] / 1000), 2)
            elif prop["id"] == "2129_0":
                self.current_limit = prop["value"]
            elif prop["id"] == "2126_0":
                self.auth_mode = self.auth_mode_as_str(prop["value"])

    def auth_mode_as_str(self, code):
        switcher = {0: "Plug and Charge", 2: "RFID"}
        return switcher.get(code, "Unknown")


class AlfenDeviceInfo:
    def __init__(self, response):
        self.identity = response["Identity"]
        self.firmware_version = response["FWVersion"]
        self.model_id = response["Model"]

        if ALFEN_PRODUCT_MAP.get(self.model_id) is None:
            self.model = self.model_id
        else:
            self.model = f"{ALFEN_PRODUCT_MAP.get(self.model_id)} " \
                         f"({self.model_id})"

        self.object_id = response["ObjectId"]
        self.type = response["Type"]
