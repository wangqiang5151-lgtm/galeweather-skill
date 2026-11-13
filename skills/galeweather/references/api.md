# GaleWeather API 接入参考

文档更新：2026-11-13。依据原《疾风气象数据API接口文档_v1.0(2)》《疾风气象要素清单_v2(2)》及本仓库客户端整理。**未经过生产接口联调**；以下区分客户端已实现行为、来源文档约定与待核验内容。

## 1. 地址与鉴权

客户端默认基础地址：https://www.galeweather.cn/api/v1/weather。原文档为同路径 HTTP，HTTPS 上线状态待服务方确认。所有调用使用 GET，单次一个坐标。

```http
Authorization: Bearer <API_KEY>
Accept: application/json
```

Key 通过环境变量 GALEWEATHER_API_KEY 读取，不放入 URL。所有模式包括 variables 都要求 Key。GALEWEATHER_BASE_URL 必须是可信基础地址，不含查询串、片段或用户名密码。客户端不跟随重定向，不自动降级 HTTP。

## 2. 接口一览

| 路径 | 必需参数 | 可选参数/默认值 | 来源文档中的结果位置 |
|---|---|---|---|
| /forecast | latitude, longitude, variables | forecast_days=15；timezone=Asia/Shanghai；interval=15m | data.records |
| /current | latitude, longitude, variables | timezone=Asia/Shanghai | data.current |
| /history | latitude, longitude, variables, start_date, end_date | timezone=Asia/Shanghai；interval=15m | data.records |
| /variables | 客户端不发送查询参数 | 无 | 具体 data 结构待核验 |

这里的 history 是历史气象数据，不代表“当时已发布的历史预测”，也不保证是目标场站仪器实测。current 同样不必然是站点实测。

当前客户端仅实现上述四种模式。不要把其他版本 API、45 天预测、历史逐日起报窗口或 EEE/GFP 筛选参数套入本客户端；相关能力需服务方另行提供已核验接口文档。

## 3. 参数约束

| HTTP 参数 | CLI 参数 | 已实现行为 | 服务端待核验项 |
|---|---|---|---|
| latitude | --latitude | 必填有限数值，[-90,90] | 坐标系、精度、授权范围 |
| longitude | --longitude | 必填有限数值，[-180,180] | 同上；不接受批量坐标 |
| variables | --variables | 英文逗号分隔，无空格；保留 hPa 大小写；客户端只校验名称格式 | 最大数量、字段权限、部分失败规则 |
| forecast_days | --forecast-days | 仅 forecast；默认15，整数1—15 | 起报边界、更新频率、结束时刻 |
| start_date/end_date | --start-date/--end-date | 仅 history；有效 YYYY-MM-DD，结束日不早于开始日 | 最早可查日期、延迟、单次跨度上限 |
| timezone | --timezone | 默认 Asia/Shanghai；variables 模式不发送 | 支持的时区、非法值处理 |
| interval | 无 | forecast/history 固定发送15m；current不发送 | 是否有其他粒度；原生/插值/重采样 |

来源文档建议历史单次小于 5 年，但这不是服务端确定上限，也不是试用授权承诺。客户端没有历史跨度上限校验；首次建议只查一天，再根据授权分批。

CLI 附加参数：--timeout 默认60秒，范围 (0,300]；--output 指定文件，父目录需存在且文件不可已存在。响应体超过64MiB时客户端拒绝处理，应缩短日期或减少字段。

## 4. 时间与结果解释

来源文档规定时间为含时区的 ISO8601。历史查询包含起止日，默认每日00:00—23:45；这些口径仍需与线上样例核对。预测从当天时间点开始，不应假设从00:00起报，也不要未经验证就按“天数×96”断言记录数。

解析时区分数据有效时间和预报起报时间；若响应没有起报时间，不要自行补造。时间键名称、排序、更新周期、缺测标记、空结果规则目前尚无完整线上样例。

| 字段 | 文档约定/当前客户端行为 |
|---|---|
| code | 必须为整数；0成功，非0触发客户端错误 |
| message | 来源文档约定的说明字段；客户端未强制校验 |
| request_id | 来源文档约定的追踪字段；客户端未强制校验 |
| data | 成功时必须存在且不为null；客户端未校验内部业务结构 |
| data.records | forecast/history 的来源文档约定；记录字段待核验 |
| data.current | current 的来源文档约定；内部结构待核验 |

下面仅展示**人工构造的最小响应外壳**，不是线上返回或非空记录结构，不可用作数据质量验收依据：

```json
{
  "code": 0,
  "message": "示意：成功",
  "request_id": "EXAMPLE_NOT_A_REAL_REQUEST",
  "data": {
    "records": []
  }
}
```

空数组在此只用于说明结构，不表示线上无数据时一定返回成功。禁止将缺测擅自补0，禁止将空结果当作晴天、静风或零发电。

正式联调需补：forecast/history 连续两条真实脱敏记录、current完整对象、variables完整结构，以及缺测、空数据和失败响应。未取得样例前，不猜测记录内时间键、单位容器或缺测哨兵值。

## 5. 字段支持边界

[variables.json](variables.json) 是235项文档候选清单，forecast/history 布尔值来自来源文档，不是实时可用状态，也没有 current 支持矩阵。/variables 是否返回全平台清单还是当前 Key 权限内清单，待服务方确认。

原来源存在冲突：PDF列10—200m每10m风速/风向，Word建议10、30…170m并将200m作不支持示例。200m等字段需逐项核验。气压层和部分瞬时辐射没有历史支持；weather_code在原Word中仅为未来接入项目。clear_sky_ghi/dni 的业务定义待确认。

更多物理含义见[风光字段说明](../../../docs/wind-solar-fields.md)。完整请求见[示例](../../../examples/README.md)。

## 6. 错误与授权

来源文档的业务码见[错误排查](../../../docs/errors.md)。HTTP状态码与业务码不是一套编号，二者映射尚未联调核验；业务失败也可能出现在HTTP成功响应中。

发行、有效期、停用、接口权限、IP/坐标范围和配额由服务端执行。试用额度与计量方式见[试用确认表](../../../docs/trial-and-quota.md)，不要从客户端参数范围推断套餐权限。
