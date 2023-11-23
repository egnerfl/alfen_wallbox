# Alfen Wallbox - HomeAssistant Integration

This is a custom component to allow control of Alfen Wallboxes in [HomeAssistant](https://home-assistant.io).

The component is a fork of the [Garo Wallbox custom integration](https://github.com/sockless-coding/garo_wallbox).

![Screenshot](https://github.com/egnerfl/alfen_wallbox/blob/master/doc/Screen%20Shot%202022-06-01%20at%2013.34.44.png)

> After reverse engineering the API myself I found out that there is already a python libary wrapping the Alfen API.
> https://gitlab.com/LordGaav/alfen-eve/-/tree/develop/alfeneve

## Installation

### Install using HACS (recomended)
If you do not have HACS installed yet visit https://hacs.xyz for installation instructions.
In HACS fist go to the Integrations section and click on the dots in the top right corner and select custom repositories. 
Enter `https://github.com/egnerfl/alfen_wallbox.git`, select "Integration" as category and click "ADD". 
Now you can hit the big + at the bottom right and search for **Alfen Wallbox**.

### Install manually
Clone or copy this repository and copy the folder 'custom_components/alfen_wallbox' into '<homeassistant config>/custom_components/alfen_wallbox'

## Configuration

Once installed the Alfen Wallbox integration can be configured via the Home Assistant integration interface 
where you can enter the IP address of the device.

### Home Assistant Energy Dashboard
The wallbox can be added to the Home Assistant Energy Dashboard using the `_meter_reading` sensor.
