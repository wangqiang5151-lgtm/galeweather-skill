import importlib.util
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error

spec = importlib.util.spec_from_file_location('weather', Path(__file__).parents[1] / 'skills/galeweather/scripts/weather.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

class Fake:
    def open(self, req, timeout):
        self.req = req
        return io.BytesIO(json.dumps({'code':0,'data':{'records':[]}}).encode())

class Tests(unittest.TestCase):
    def args(self, mode='forecast', *extra):
        return w.parser().parse_args([mode,'--latitude','36.67','--longitude','117.02','--variables','wind_speed_850hPa',*extra])

    @patch.dict(os.environ, {'GALEWEATHER_API_KEY':'test-secret-123'}, clear=True)
    def test_header_and_params(self):
        f=Fake();w.fetch(self.args(), f)
        self.assertEqual(f.req.get_header('Authorization'),'Bearer test-secret-123')
        self.assertNotIn('test-secret',f.req.full_url)
        self.assertIn('forecast_days=15',f.req.full_url)
        self.assertIn('wind_speed_850hPa',f.req.full_url)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_key(self):
        with self.assertRaises(w.ClientError):w.fetch(self.args(),Fake())

    @patch.dict(os.environ, {'GALEWEATHER_API_KEY':'test-secret','GALEWEATHER_BASE_URL':'http://www.galeweather.cn/api/v1/weather'}, clear=True)
    def test_http_requires_opt_in(self):
        with self.assertRaises(w.ClientError):w.fetch(self.args(),Fake())

    def test_invalid_coordinate(self):
        a=self.args();a.latitude=float('nan')
        with self.assertRaises(w.ClientError):w.params(a)

    def test_dates(self):
        a=self.args('history','--start-date','2026-07-10','--end-date','2026-07-01')
        with self.assertRaises(w.ClientError):w.params(a)

    def test_current_has_no_interval(self):
        self.assertNotIn('interval',w.params(self.args('current')))

    def test_forecast_bounds(self):
        with self.assertRaises(w.ClientError):w.params(self.args('forecast','--forecast-days','16'))

    def test_redirect_blocked(self):
        self.assertIsNone(w.NoRedirect().redirect_request(None,None,302,'',{},'https://elsewhere.example'))

    @patch.dict(os.environ, {'GALEWEATHER_API_KEY':'test-secret'}, clear=True)
    def test_unauthorized_safe(self):
        class Bad:
            def open(self,*a,**kw):raise urllib.error.HTTPError('https://example',401,'test-secret',{},None)
        with self.assertRaises(w.ClientError) as caught:w.fetch(self.args(),Bad())
        self.assertNotIn('test-secret',str(caught.exception))

    @patch.dict(os.environ, {'GALEWEATHER_API_KEY':'test-secret'}, clear=True)
    def test_business_failure(self):
        class Bad:
            def open(self,*a,**kw):return io.BytesIO(b'{"code":4012,"message":"test-secret","data":null}')
        with self.assertRaises(w.ClientError) as caught:w.fetch(self.args(),Bad())
        self.assertNotIn('test-secret',str(caught.exception))

if __name__=='__main__':unittest.main()
