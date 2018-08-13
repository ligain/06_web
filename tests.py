import json
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError

from ip2w import (
    CONFIG_PATH,
    get_geo_cords, get_weather,
    HOST, PORT
)


class TestGeoCords(unittest.TestCase):
    def setUp(self):
        with open(CONFIG_PATH) as conf_file:
            config_dict = json.load(conf_file)
            self.api_token = config_dict['IPINFO_TOKEN']
        self.config = {
            'IPINFO_TOKEN': self.api_token
        }
        self.ip = '12.45.76.90'

    def test_empty_token(self):
        geo_resp = get_geo_cords(self.ip, {})
        self.assertTupleEqual(geo_resp, (None, None))
        geo_resp2 = get_geo_cords(self.ip, {'IPINFO_TOKEN': {}})
        self.assertTupleEqual(geo_resp2, (None, None))

    def test_success_response(self):
        lat, long = get_geo_cords(self.ip, self.config)
        float(lat)
        float(long)


class TestGetWeather(unittest.TestCase):
    def setUp(self):
        with open(CONFIG_PATH) as conf_file:
            config_dict = json.load(conf_file)
            self.api_token = config_dict['OPENWEATHERMAP_TOKEN']
        self.config = {
            'OPENWEATHERMAP_TOKEN': self.api_token
        }
        self.cords = ('37.3859', '-122.0838')

    def test_empty_token(self):
        weather_resp = get_weather(*self.cords, {})
        self.assertIsNone(weather_resp)
        weather_resp2 = get_weather(
            *self.cords,
            {'OPENWEATHERMAP_TOKEN': ''}
        )
        self.assertIsNone(weather_resp2)

    def test_bad_token(self):
        weather_resp = get_weather(
            *self.cords,
            {'OPENWEATHERMAP_TOKEN': 'bad_token'}
        )
        self.assertIsNone(weather_resp)

    def test_success_response(self):
        weather_resp = get_weather(*self.cords, self.config)
        self.assertIsInstance(weather_resp, dict)
        self.assertIn('weather', weather_resp)


class TestApp(unittest.TestCase):
    """
    While running this test ip2w.py should be up and
    running on `HOST` and `PORT`
    """

    def test_bad_url(self):
        with self.assertRaises(HTTPError):
            urlopen('http://{}:{}'.format(HOST, PORT))
            urlopen('http://{}:{}/ip2w/'.format(HOST, PORT))
            urlopen('http://{}:{}/ip2w/999.0.0.0'.format(HOST, PORT))
            urlopen('http://{}:{}/ip2w/1'.format(HOST, PORT))
            urlopen('http://{}:{}/ip2w/1.1.1'.format(HOST, PORT))

    def test_successful_case(self):
        resp = urlopen('http://{}:{}/ip2w/8.8.8.8'.format(HOST, PORT))
        self.assertEqual(resp.status, 200)


if __name__ == '__main__':
    unittest.main()
