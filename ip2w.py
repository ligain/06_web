#!/usr/bin/env python3

import logging
import re
import os
import json
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError


# CONFIG_PATH = '/usr/local/etc/ip2w/ip2w_config.json'
CONFIG_PATH = './ip2w_config.json'
HOST = 'localhost'
PORT = 8080
URL_REGEX = r'ip2w/((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)' \
        r'{3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))/?$'


def get_geo_cords(ip, config):
    """
    Retrieve latitude and longitude of server which
    has specific IP.
    If an error occurs the result will look like: (None, None)
    :param ip: str
    :param config: dict
    :return: (latitude: str, longitude: str): tuple
    """
    token = config.get('IPINFO_TOKEN')
    if not token:
        logging.error("IPINFO_TOKEN was not found in config")
        return None, None
    url = "https://ipinfo.io/{}/geo?token={}".format(ip, token)
    req = Request(url=url)
    try:
        with urlopen(req) as resp:
            resp_dict = json.load(resp)
            geo_cords = resp_dict.get('loc')
            return geo_cords.split(',')
    except HTTPError as e:
        logging.error("Url: {} returned error: {}".format(url, str(e)))
        return None, None


def get_weather(latitude, longitude, config):
    """
    Retrieve weather info from openweathermap API
    :param latitude: str
    :param longitude: str
    :param config: dict
    :return: dict or None
    """
    token = config.get('OPENWEATHERMAP_TOKEN')
    if not token:
        logging.error("OPENWEATHERMAP_TOKEN was not found in config")
        return
    request_params = urlencode({
        'APPID': token,
        'lat': latitude,
        'lon': longitude,
        'lang': 'ru',
        'units': 'metric'
    })
    url = "https://api.openweathermap.org/data/2.5/weather?{}".format(request_params)
    req = Request(url=url)
    try:
        with urlopen(req) as resp:
            resp_dict = json.load(resp)
            return resp_dict
    except HTTPError as e:
        logging.error("Url: {} returned error: {}".format(url, str(e)))


def weather_handler(ip, config=None):
    if not ip:
        logging.error("IP address is missing")
        return
    if not config:
        logging.error("Config was not found")
        return
    latitude, longitude = get_geo_cords(ip, config)
    if not latitude or not longitude:
        logging.error("Wrong latitude or longitude received from ipinfo.io service")
        return
    weather_dict = get_weather(latitude, longitude, config)
    result_dict = {
        'city': weather_dict.get('name'),
        'temp': weather_dict.get('main', {}).get('temp', ''),
        'conditions': weather_dict.get('weather', {})[0].get('description', '')
    }
    return json.dumps(result_dict).encode()


def send_response(code, status, start_response, headers, content=b''):
    status_string = '{} {}'.format(code, status.upper())
    heads = list(zip(headers.keys(), headers.values()))
    start_response(status_string, heads)
    return [content]


def application(env, start_response):

    if not os.path.isfile(CONFIG_PATH):
        raise RuntimeError("Config was not found on "
                           "path: {}".format(CONFIG_PATH))

    with open(CONFIG_PATH) as conf_file:
        config = json.load(conf_file)
    # TODO perrmission denied
    # dictConfig(config['LOGGER_CONF'])

    path = env.get('PATH_INFO', '').lstrip('/')
    match = re.search(URL_REGEX, path)
    if match is not None:
        ip = match.groups(1)
        resp_content = weather_handler(ip, config)
        if resp_content is None:
            return send_response(
                500, 'Internal Server Error',
                start_response,
                headers={"Content-Type": 'text/plain'},
            )
        return send_response(
            200, 'OK',
            start_response,
            headers={"Content-Type": 'application/json; charset=utf-8'},
            content=resp_content
        )
    return send_response(
        404, 'Not Found',
        start_response,
        headers={"Content-Type": 'text/plain'},
        content=b'Not Found'
    )


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server(HOST, PORT, application)
    srv.serve_forever()
