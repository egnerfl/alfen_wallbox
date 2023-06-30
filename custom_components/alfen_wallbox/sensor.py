import logging

import voluptuous as vol

from homeassistant.const import (
    CONF_ICON, 
    CONF_NAME, 
    TEMP_CELSIUS)
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    PLATFORM_SCHEMA,
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_MEASUREMENT,
    SensorEntity,
)
from homeassistant.helpers import config_validation as cv, entity_platform, service

from . import DOMAIN as ALFEN_DOMAIN

from .alfen import AlfenDevice
from .const import SERVICE_REBOOT_WALLBOX, SERVICE_SET_CURRENT_LIMIT, SERVICE_ENABLE_RFID_AUTHORIZATION_MODE, SERVICE_DISABLE_RFID_AUTHORIZATION_MODE

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    pass


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up using config_entry."""
    device = hass.data[ALFEN_DOMAIN].get(entry.entry_id)
    async_add_entities([
        AlfenMainSensor(device),
        AlfenSensor(device, 'Status Code', 'status'),
        AlfenSensor(device, 'Uptime', 'uptime', 's'),
        AlfenSensor(device, 'Bootups', 'bootups'),
        AlfenSensor(device, "Voltage L1", 'voltage_l1', "V"),
        AlfenSensor(device, "Voltage L2", 'voltage_l2', "V"),
        AlfenSensor(device, "Voltage L3", 'voltage_l3', "V"),
        AlfenSensor(device, "Current L1", 'current_l1', "A"),
        AlfenSensor(device, "Current L2", 'current_l2', "A"),
        AlfenSensor(device, "Current L3", 'current_l3', "A"),
        AlfenSensor(device, "Active Power Total", 'active_power_total', "W"),
        AlfenSensor(device, "Meter Reading", 'meter_reading', "kWh"),
        AlfenSensor(device, "Temperature", 'temperature', TEMP_CELSIUS),
        AlfenSensor(device, "Current Limit", 'current_limit', "A"),
        AlfenSensor(device, 'Authorization Mode', 'auth_mode'),
    ])

    platform = entity_platform.current_platform.get()

    platform.async_register_entity_service(
        SERVICE_REBOOT_WALLBOX,
        {},
        "async_reboot_wallbox",
    )

    platform.async_register_entity_service(
        SERVICE_SET_CURRENT_LIMIT,
        {
            vol.Required('limit'): cv.positive_int,
        },
        "async_set_current_limit",
    )

    platform.async_register_entity_service(
        SERVICE_ENABLE_RFID_AUTHORIZATION_MODE,
        {},
        "async_enable_rfid_auth_mode",
    )

    platform.async_register_entity_service(
        SERVICE_DISABLE_RFID_AUTHORIZATION_MODE,
        {},
        "async_disable_rfid_auth_mode",
    )

class AlfenMainSensor(Entity):
    def __init__(self, device: AlfenDevice):
        """Initialize the sensor."""
        self._device = device
        self._name = f"{device.name}"
        self._sensor = "sensor"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._device.id}-{self._sensor}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        return "mdi:car-electric"

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._device.status is not None:
            return self.status_as_str()
        return None

    async def async_reboot_wallbox(self):
        await self._device.reboot_wallbox()

    async def async_set_current_limit(self, limit):
        await self._device.set_current_limit(limit)

    async def async_enable_rfid_auth_mode(self):
        await self._device.set_rfid_auth_mode(True)               

    async def async_disable_rfid_auth_mode(self):
        await self._device.set_rfid_auth_mode(False)

    async def async_update(self):
        await self._device.async_update()

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device.device_info 

    def status_as_str(self):
        switcher = {
            4: "Available",
            7: "Cable connected",
            10: "Vehicle connected",
            11: "Charging",
            17: "Session end", #(Unit with socket only?) Cable still connected to EVSE after charging, but car disconnected. Screen shows charging stats until cable disconnected from EVSE.
            34: "Blocked", #EVSE is blocked through management interface of CPO.
            36: "Paused",
            41: "Solar charging",
        }
        return switcher.get(self._device.status.status, "Unknown")

class AlfenSensor(SensorEntity):
    def __init__(self, device: AlfenDevice, name, sensor, unit = None):
        """Initialize the sensor."""
        self._device = device
        self._name = f"{device.name} {name}"
        self._sensor = sensor
        self._unit = unit
        if self._sensor == "active_power_total":
            _LOGGER.info(f'Initiating State sensors {self._name}')
            self._attr_device_class = DEVICE_CLASS_POWER
            self._attr_state_class = STATE_CLASS_MEASUREMENT
        elif self._sensor == "uptime":
            _LOGGER.info(f'Initiating State sensors {self._name}')
            self._attr_state_class = STATE_CLASS_TOTAL_INCREASING
        elif self._sensor == "meter_reading":
            _LOGGER.info(f'Initiating State sensors {self._name}')
            self._attr_device_class = DEVICE_CLASS_ENERGY
            self._attr_state_class = STATE_CLASS_TOTAL_INCREASING            

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._device.id}-{self._sensor}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        icon = None
        if self._sensor == "temperature":
            icon = "mdi:thermometer"
        elif self._sensor.startswith('current_'):
            icon = "mdi:flash"
        elif self._sensor.startswith('voltage_'):
            icon = "mdi:flash-outline"
        elif self._sensor == "uptime":
            icon = "mdi:timer-outline"     
        elif self._sensor == "bootups":
            icon = "mdi:reload"       
        elif self._sensor == "active_power_total":
            icon = "mdi:circle-slice-3"                            
        return icon

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return round(self.state, 2)

    @property
    def native_unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._device.status.__dict__[self._sensor]

    @property
    def unit_of_measurement(self):
        return self._unit

    async def async_update(self):
        await self._device.async_update()

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device.device_info
