#!/usr/bin/env python3
"""GaleWeather API client. Python 3.10+, standard library only."""
import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


class ClientError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['forecast', 'current', 'history', 'variables'])
    p.add_argument('--latitude', type=float)
    p.add_argument('--longitude', type=float)
    p.add_argument('--variables')
    p.add_argument('--forecast-days', type=int)
    p.add_argument('--start-date')
    p.add_argument('--end-date')
    p.add_argument('--timezone', default='Asia/Shanghai')
    p.add_argument('--output', type=Path)
    p.add_argument('--timeout', type=float, default=60)
    return p


def params(a):
    if not math.isfinite(a.timeout) or not 0 < a.timeout <= 300:
        raise ClientError('timeout 必须在 (0,300] 秒内')
    if a.mode == 'variables':
        if any(v is not None for v in [a.latitude, a.longitude, a.variables, a.forecast_days, a.start_date, a.end_date]):
            raise ClientError('variables 查询不接受坐标、要素或日期参数')
        return {}
    for name, value, limit in [('latitude', a.latitude, 90), ('longitude', a.longitude, 180)]:
        if value is None or not math.isfinite(value) or abs(value) > limit:
            raise ClientError(f'{name} 缺失或超出范围')
    if not a.variables or not re.fullmatch(r'[a-z][a-zA-Z0-9_]*(,[a-z][a-zA-Z0-9_]*)*', a.variables):
        raise ClientError('variables 应为英文逗号分隔的字段名，保留 hPa 等大小写')
    q = dict(latitude=a.latitude, longitude=a.longitude, variables=a.variables, timezone=a.timezone)
    if a.mode != 'current':
        q['interval'] = '15m'
    if a.mode == 'forecast':
        days = a.forecast_days if a.forecast_days is not None else 15
        if not 1 <= days <= 15:
            raise ClientError('forecast_days 范围为1至15')
        q['forecast_days'] = days
    elif a.forecast_days is not None:
        raise ClientError('forecast-days 只用于 forecast')
    if a.mode == 'history':
        try:
            if not all(x and re.fullmatch(r'\d{4}-\d{2}-\d{2}', x) for x in [a.start_date, a.end_date]):
                raise ValueError()
            start, end = map(dt.date.fromisoformat, [a.start_date, a.end_date])
        except ValueError:
            raise ClientError('历史日期必须为有效的 YYYY-MM-DD') from None
        if end < start:
            raise ClientError('结束日期不能早于开始日期')
        q.update(start_date=a.start_date, end_date=a.end_date)
    elif a.start_date is not None or a.end_date is not None:
        raise ClientError('起止日期只用于 history')
    return q


def fetch(a, opener=None):
    q = params(a)
    key = os.environ.get('GALEWEATHER_API_KEY', '').strip()
    if not key:
        raise ClientError('请在本机设置 GALEWEATHER_API_KEY；不要在聊天中发送 Key')
    if any(ord(c) < 33 or ord(c) > 126 for c in key):
        raise ClientError('Key 含不支持的字符')
    base = os.environ.get('GALEWEATHER_BASE_URL', 'https://www.galeweather.cn/api/v1/weather').rstrip('/')
    u = urllib.parse.urlsplit(base)
    if u.scheme not in ('http', 'https') or not u.hostname or u.username or u.password or u.query or u.fragment:
        raise ClientError('GALEWEATHER_BASE_URL 格式不正确')
    if u.scheme == 'http' and os.environ.get('GALEWEATHER_ALLOW_HTTP') != '1':
        raise ClientError('HTTP 会明文传输 Key；请启用 HTTPS，或自行设置 GALEWEATHER_ALLOW_HTTP=1')
    url = base + '/' + a.mode
    if q:
        url += '?' + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + key, 'Accept': 'application/json', 'User-Agent': 'galeweather-skill/1.0'})
    opener = opener or urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(req, timeout=a.timeout) as res:
            raw = res.read(64 * 1024 * 1024 + 1)
        if len(raw) > 64 * 1024 * 1024:
            raise ClientError('响应超过64MiB，请缩短日期范围或减少要素')
        result = json.loads(raw)
    except urllib.error.HTTPError as e:
        hints = {401: 'Key 缺失、无效或过期', 403: 'Key 停用、权限不足或IP限制', 404: '接口未上线或无数据', 429: '超过限流，请稍后再试'}
        raise ClientError(f'HTTP {e.code}: ' + hints.get(e.code, '请求失败；重定向不会被跟随')) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ClientError('网络或TLS连接失败，请检查服务地址和网络；不会自动降级HTTP') from None
    except (ValueError, UnicodeError):
        raise ClientError('服务返回的内容不是有效JSON') from None
    if not isinstance(result, dict) or type(result.get('code')) is not int:
        raise ClientError('响应不符合 code/message/request_id/data 结构')
    if result['code'] != 0:
        raise ClientError(f"业务错误码 {result['code']}；请核对授权、参数和数据可用性")
    if 'data' not in result or result['data'] is None:
        raise ClientError('成功响应缺少 data')
    # Defensive redaction if the remote service accidentally echoes a credential.
    return json.loads(json.dumps(result, ensure_ascii=False).replace(key, '[REDACTED]'))


def main():
    a = parser().parse_args()
    try:
        if a.output and a.output.exists():
            raise ClientError('输出文件已存在，请选择新文件名')
        result = fetch(a)
        text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if a.output:
            with a.output.open('x', encoding='utf-8') as f:
                f.write(text)
        else:
            print(text, end='')
        return 0
    except (ClientError, OSError) as e:
        msg = str(e) if isinstance(e, ClientError) else '无法写入输出文件'
        print(json.dumps({'error': msg}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
