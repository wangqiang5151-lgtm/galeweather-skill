# 疾风气象 GaleWeather Skill

通过授权 API 查询单点气象预测、当前天气和历史数据，为风电、光伏及一般气象应用提供接入工具。Python 3.10+，仅使用标准库。

本仓库提供客户端与接入文档，不包含气象 API 服务端或预测算法。代码公开不代表数据免费，也不自动授予代码或数据的商业使用权。

## 开始使用

1. 通过本页联系方式申请试用，确认接口、坐标范围、要素、有效期和额度。
2. 下载仓库并按[快速开始](docs/quickstart.md)配置本机环境变量。
3. 从一个坐标、一天、少量要素开始调用。
4. 根据 [API 参考](skills/galeweather/references/api.md)和[风光字段说明](docs/wind-solar-fields.md)解析结果。

**验证状态（2026-11-13）**：文档参数已按当前客户端核对；未使用真实 Key 完成生产联调。默认 HTTPS 地址、接口上线状态、字段权限和额度需由服务方确认。静态要素清单不是线上可用性承诺。

## 调用示例

以下命令在仓库根目录执行，前提是已设置有效的 GALEWEATHER_API_KEY；Linux/macOS 可将 python 换为 python3。

风电：一天的 70 米风速和风向。

```bash
python skills/galeweather/scripts/weather.py forecast --latitude 36.67 --longitude 117.02 --variables wind_speed_70m,wind_direction_70m --forecast-days 1
```

光伏：一天的 GHI、DNI 和 DHI。

```bash
python skills/galeweather/scripts/weather.py forecast --latitude 36.67 --longitude 117.02 --variables shortwave_radiation,direct_normal_irradiance,diffuse_radiation --forecast-days 1
```

脚本成功退出 0；运行错误退出 1；命令行语法错误退出 2。结果为格式化 JSON，可能进行凭据脱敏。不会自动重试；输出文件已存在时拒绝覆盖。

## 文档导航

| 文档 | 内容 |
|---|---|
| [快速开始](docs/quickstart.md) | 下载、Windows/Bash 配置、首次调用、宿主安装 |
| [API 参考](skills/galeweather/references/api.md) | 地址、鉴权、四接口、参数、返回与时间口径 |
| [请求示例](examples/README.md) | CLI、curl、PowerShell 原生 HTTP |
| [风光字段](docs/wind-solar-fields.md) | 风速高度、风向、辐照度与候选字段限制 |
| [试用与额度](docs/trial-and-quota.md) | 授权确认表、计量规则与试用验收 |
| [错误排查](docs/errors.md) | HTTP、业务码、CLI 错误及支持信息 |
| [候选要素清单](skills/galeweather/references/variables.json) | 235 项文档候选要素，不是实际授权清单 |
| [维护与验证](docs/maintainer-release.md) | 离线测试、联调清单及文档发布要求 |

## 联系与试用

扫描二维码联系疾风气象服务提供方。申请时说明用途、区域或坐标、所需字段、历史/预测类型、预计点位数和每日频次。不要在公开 Issue、聊天或源码中提供 Key。

<img src="assets/contact-wechat.jpg" alt="疾风气象微信联系二维码" width="360" />

Key 由服务端管理，接口、地域、有效期和额度以实际授权为准。当前没有在本仓库公布自助注册或购买接口；代码许可由权利人确定，气象数据使用权另按服务授权约定。
