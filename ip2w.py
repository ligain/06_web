#!/usr/bin/env python3

import logging
import re
import os
import json
import urllib
from functools import wraps
from urllib.request import urlopen, Request
from urllib.parse import urlencode, urljoin
from urllib.error import HTTPError


# import sys
# sys.path.append('/opt/pycharm-2017.3.4/debug-eggs/pycharm-debug-py3k.egg')
# import pydevd
# pydevd.settrace('localhost', port=9091, stdoutToServer=True, stderrToServer=True)


# CONFIG_PATH = '/usr/local/etc/ip2w_config.json'
from logging.config import dictConfig

CONFIG_PATH = '/home/linder/PycharmProjects/otus-python/06_web/homework/ip2w_config.json'


def get_geo_cords(env, ip):
    """
    Retrieve latitude and longitude of server which
    has specific IP.
    If an error occurs the result will look like: (None, None)
    :param ip: str
    :return: (latitude: str, longitude: str): tuple
    """
    cfg = env.get('ip2w.config')
    if not cfg:
        logging.error("Config was not found")
        return None, None
    token = cfg.get('IPINFO_TOKEN')
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


def get_weather(env, latitude, longitude):
    """
    Retrieve weather info from openweathermap API
    :param env: dict
    :param latitude: str
    :param longitude: str
    :return: dict or None
    """
    cfg = env.get('ip2w.config')
    if not cfg:
        logging.error("Config was not found")
        return
    token = cfg.get('OPENWEATHERMAP_TOKEN')
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


def weather_handler(env, start_response):
    ip_param = env.get('ip2w.url_args')
    if not ip_param:
        return send_response(
            400, 'Bad Request',
            start_response,
            headers={"Content-Type": 'text/plain'},
            content=b'Bad Request'
        )
    ip = ip_param[0]
    latitude, longitude = get_geo_cords(env, ip)
    if not latitude or not longitude:
        logging.error("Wrong latitude or longitude received from ipinfo.io service")
        return send_response(
            500, 'Internal Server Error',
            start_response,
            headers={"Content-Type": 'text/plain'},
        )
    weather_dict = get_weather(env, latitude, longitude)
    result_dict = {
        'city': weather_dict.get('name'),
        'temp': weather_dict.get('main', {}).get('temp', ''),
        'conditions': weather_dict.get('weather', {})[0].get('description', '')
    }
    resp_content = json.dumps(result_dict).encode()
    return send_response(
        200, 'OK',
        start_response,
        headers={"Content-Type": 'application/json; charset=utf-8'},
        content=resp_content
    )


URLS = [
    (r'ip2w/((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
     r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))/?$', weather_handler)
]


def send_response(code, status, start_response, headers, content=b''):
    status_string = '{} {}'.format(code, status.upper())
    heads = list(zip(headers.keys(), headers.values()))
    start_response(status_string, heads)
    return [content]


def config_middleware(config_path=None):
    def wrap(app):
        @wraps(app)
        def wrapper(env, start_response):
            if not os.path.isfile(config_path):
                raise RuntimeError("Config was not found on "
                                   "path: {}".format(config_path))
            with open(config_path) as conf_file:
                config_dict = json.load(conf_file)
            # TODO perrmission denied
            # dictConfig(config_dict['LOGGER_CONF'])
            env['ip2w.config'] = config_dict
            return app(env, start_response)
        return wrapper
    return wrap


def router_middleware(urlpatterns=None):
    def wrap(app):
        @wraps(app)
        def wrapper(env, start_response):
            path = env.get('PATH_INFO', '').lstrip('/')
            for regex, handler in urlpatterns:
                match = re.search(regex, path)
                if match is not None:
                    env['ip2w.url_args'] = match.groups()
                    return handler(env, start_response)
            return send_response(
                404, 'Not Found',
                start_response,
                headers={"Content-Type": 'text/plain'},
                content=b'Not Found'
            )
        return wrapper
    return wrap


@config_middleware(config_path=CONFIG_PATH)
@router_middleware(urlpatterns=URLS)
def application(env, start_response):
    pass


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
