#!/usr/bin/env python3
import argparse
import os
import sys

import requests


LIGHT_IP = os.environ.get('ELGATO_LIGHT_IP', '192.168.68.117')

_http_timeout = 5
_base_url = f"http://{LIGHT_IP}:9123"

session = requests.Session()
session.headers.update({'Content-Type': 'application/json'})


class ElgatoLight:
    ip_address: str = ""
    brightness: int = 0
    temperature: int = 0
    is_on: bool = False

    @classmethod
    def get_commands(cls):
        _methods = [method for method in dir(cls) if callable(getattr(cls, method)) and not method.startswith('_') and not method.startswith('scene_')]
        _methods += ['scene']
        return _methods

    @classmethod
    def get_scenes(cls):
        _scenes = [method for method in dir(cls) if callable(getattr(cls, method)) and method.startswith('scene_')]
        _scenes = [scene[6:] for scene in _scenes]
        return _scenes

    def __init__(self, ip_address: str):
        self.ip_address = ip_address
        self._update()

    def _update(self):
        response = session.get(f"http://{self.ip_address}:9123/elgato/lights", timeout=_http_timeout)
        data = response.json()
        lights = data.get('lights', [])
        if len(lights) <= 0:
            return
        data = lights[0]
        self.brightness = data.get('brightness', 0)
        self.temperature = data.get('temperature', 0)
        self.is_on = bool(data.get('on', False))

    def _power(self, on: bool):
        query = {
            "lights": [
                {
                    "on": int(on)
                }
            ]
        }
        response = session.put(f"{_base_url}/elgato/lights", json=query, timeout=_http_timeout)
        self._update()

    def toggle(self):
        self._power(not self.is_on)

    def on(self):
        self._power(True)

    def off(self):
        self._power(False)

    def _set_brightness(self, brightness):
        query = {
            "lights": [
                {
                    "brightness": brightness
                }
            ]
        }
        response = session.put(f"{_base_url}/elgato/lights", json=query, timeout=_http_timeout)
        self._update()

    def _set_temperature(self, temperature):
        query = {
            "lights": [
                {
                    "temperature": temperature
                }
            ]
        }
        response = session.put(f"{_base_url}/elgato/lights", json=query, timeout=_http_timeout)
        self._update()

    def _set_scene(self, temp, brightness):
        query = {
            "lights": [
                {
                    "temperature": temp,
                    "brightness": brightness,
                }
            ]
        }
        response = session.put(f"{_base_url}/elgato/lights", json=query, timeout=_http_timeout)
        self._update()

    def bright(self):
        self._set_brightness(50)

    def brighter(self):
        self._set_brightness(self.brightness + 10)

    def dim(self):
        self._set_brightness(30)

    def dimmer(self):
        self._set_brightness(self.brightness - 10)

    def warm(self):
        self._set_temperature(272)

    def cool(self):
        self._set_temperature(200)

    def warmer(self):
        self._set_temperature(self.temperature + 10)

    def cooler(self):
        self._set_temperature(self.temperature - 10)

    def scene_evening(self):
        self._set_scene(272, 30)

    def scene_daytime(self):
        self._set_scene(200, 50)


if __name__ == '__main__':
    light = ElgatoLight(LIGHT_IP)

    methods = light.get_commands()
    scenes = light.get_scenes()

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=methods, help='Adjust lighting')
    parser.add_argument('scene', choices=scenes, help="Select a scene", nargs='?')

    args = parser.parse_args()

    if args.command == 'scene':
        if args.scene in scenes:
            getattr(light, f"scene_{args.scene}")()
            light.on()
        else:
            # Show help
            parser.print_help()
            sys.exit(1)
    elif args.command in methods:
        getattr(light, args.command)()
    else:
        parser.print_help()
        sys.exit(1)
