# API 合约

依据用户提供的《疾风气象数据API接口文档_v1.0(2)》和《疾风气象要素清单_v2(2)》，未经过生产接口联调。

文档基础地址 `http://www.galeweather.cn/api/v1/weather`。脚本为保护 Key 默认使用同路径 HTTPS，需服务方确认 HTTPS 已开通。所有请求 GET，Authorization: Bearer 环境变量中的 Key。单次一个坐标。

| 路径 | 必需参数 | 可选参数 | 数据 |
|---|---|---|---|
| /forecast | latitude, longitude, variables | forecast_days=15（1—15）, timezone=Asia/Shanghai, interval=15m | data.records |
| /current | latitude, longitude, variables | timezone=Asia/Shanghai | data.current |
| /history | latitude, longitude, variables, start_date, end_date | timezone=Asia/Shanghai, interval=15m | data.records |
| /variables | 文档未指定 | 无 | 开放变量、单位、类型、插值标识；具体JSON结构未约定 |

统一响应为 code、message、request_id、data。code=0 成功。时间采用 ISO8601，含时区。历史日期包含起止日，默认每日00:00至23:45；预测示例从当天时间点开始，不应自行假设从00:00起报。历史文档建议单次小于5年，实际可用范围及限制以服务器为准，大范围宜分批。

业务码：4001坐标；4002变量；4003日期；4004历史范围；4010缺Token；4011无效；4012过期；4030停用；4031 IP；4032接口权限；4040无数据；4290限流；5000内部错误；5020上游；5030不可用。

完整候选要素在 variables.json。保留大小写，例如 wind_speed_850hPa。PDF支持10—200m每10m风速/风向，但Word仅建议10、30…170m，并将200m列作不支持示例；不能以任一静态文档替代服务端开放状态。PDF未列current支持范围；气压层和部分瞬时辐射无历史支持。clear_sky_ghi/dni 在PDF中标为疾风大模型GHI/DNI，应向服务方确认其业务定义，不能仅凭字段名假定含义。weather_code仅在Word列为未来接入项目。

Key 的发行、过期、可用接口、配额、站点范围和停用由服务端执行；本技能不发行Key、不绕过限制、不缓存凭据。没有Key时仍可查看本地要素文档。
