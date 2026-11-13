# 请求示例

先完成[配置](../docs/quickstart.md)。以下命令与当前客户端参数一致，但尚未以真实Key联调。替换为已授权坐标和字段；历史示例日期也须在授权范围内。默认HTTPS上线情况待服务方确认。

## CLI：四个接口

在仓库根目录执行；Linux/macOS可将python替换为python3。

```bash
python skills/galeweather/scripts/weather.py forecast --latitude 36.67 --longitude 117.02 --variables wind_speed_70m,wind_direction_70m --forecast-days 1
python skills/galeweather/scripts/weather.py forecast --latitude 36.67 --longitude 117.02 --variables shortwave_radiation,direct_normal_irradiance,diffuse_radiation --forecast-days 1
python skills/galeweather/scripts/weather.py current --latitude 36.67 --longitude 117.02 --variables temperature_2m,relative_humidity_2m
python skills/galeweather/scripts/weather.py history --latitude 36.67 --longitude 117.02 --variables shortwave_radiation,diffuse_radiation --start-date 2026-07-01 --end-date 2026-07-01
python skills/galeweather/scripts/weather.py variables
```

添加 --output result.json 可保存结果，文件必须不存在。不要默认五条命令都免费，也不要批量执行未经授权的点位。

## Bash：原始HTTP请求

前提：已设置GALEWEATHER_API_KEY；此例使用默认HTTPS基础地址。

```bash
curl --get 'https://www.galeweather.cn/api/v1/weather/forecast' \
  --header "Authorization: Bearer ${GALEWEATHER_API_KEY}" \
  --header 'Accept: application/json' \
  --data-urlencode 'latitude=36.67' \
  --data-urlencode 'longitude=117.02' \
  --data-urlencode 'variables=wind_speed_70m,wind_direction_70m' \
  --data-urlencode 'forecast_days=1' \
  --data-urlencode 'timezone=Asia/Shanghai' \
  --data-urlencode 'interval=15m' \
  --connect-timeout 10 --max-time 60
```

curl输出需自行核对HTTP状态和JSON业务code；不要只根据进程退出码判断业务成功。不要启用详细请求日志或将包含授权头的诊断输出公开。

## PowerShell：原始HTTP请求

适用于Windows PowerShell 5.1或PowerShell 7；Key已由快速开始设置到环境变量。

```powershell
$headers = @{
    Authorization = "Bearer $env:GALEWEATHER_API_KEY"
    Accept = 'application/json'
}
$uri = 'https://www.galeweather.cn/api/v1/weather/forecast?latitude=36.67&longitude=117.02&variables=wind_speed_70m%2Cwind_direction_70m&forecast_days=1&timezone=Asia%2FShanghai&interval=15m'
$result = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers -TimeoutSec 60 -MaximumRedirection 0
if ($null -eq $result.code -or $result.code -ne 0) {
    throw 'API返回缺少成功业务码，请核对响应和授权'
}
$result | ConvertTo-Json -Depth 20
Remove-Variable headers
```

这是原始HTTP调用，不具备weather.py的全部大小限制、脱敏和业务结构检查。不要打印或分享headers变量。

## 其他接口的HTTP参数组合

| 路径 | 查询参数 |
|---|---|
| /current | latitude=36.67、longitude=117.02、variables=temperature_2m,relative_humidity_2m、timezone=Asia/Shanghai |
| /history | latitude=36.67、longitude=117.02、variables=shortwave_radiation,diffuse_radiation、start_date=2026-07-01、end_date=2026-07-01、timezone=Asia/Shanghai、interval=15m |
| /variables | 无查询参数；仍发送Authorization头 |

不要给current发送forecast_days、日期或interval。所有逗号、时区和日期由所用HTTP库正确编码。

## 返回如何读取

forecast/history按来源文档使用data.records，current使用data.current；variables内部结构尚待确认。完整说明见[API返回章节](../skills/galeweather/references/api.md)。

当前没有已验证的生产响应文件，故不提供伪装成实测的气象数值样例。维护者取得授权后应将脱敏样例补入examples/responses/，包含核验日期、接口版本、单位和缺测说明；该目录尚未随本次文档发布创建。
