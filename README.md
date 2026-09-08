# 疾风气象 GaleWeather Skill

让支持文件型 Skill 的 AI 助手通过授权 API 获取气象预测、当前天气、历史数据。适用于新能源风光场站及一般气象查询。Python 3.10+，无第三方运行依赖。

## 包结构

- `skills/galeweather/`：可安装技能，含 SKILL.md、API客户端与要素参考。
- `tests/`：离线接口行为测试，无需真实Key，不消耗调用额度。
- `.env.example`：环境变量示例（不会自动加载）。

## 安装和配置

将 `skills/galeweather` 整个目录复制到支持 SKILL.md 的宿主技能目录，具体位置遵循宿主说明。也可直接运行脚本。仅上传到GitHub不会使所有AI产品自动具备调用能力，宿主必须支持技能、Python执行和网络访问。

向疾风气象服务提供方申请有效 API Key。当前文档未提供自助申请网址，勿假定存在注册或购Key接口。Key 不包含在本项目中，公开代码不意味着数据免费。

PowerShell 当前会话（隐藏输入）：

```powershell
$credential = Get-Credential -UserName api -Message '在密码框输入疾风气象 API Key'
$env:GALEWEATHER_API_KEY = $credential.GetNetworkCredential().Password
python skills/galeweather/scripts/weather.py forecast --latitude 36.67 --longitude 117.02 --variables wind_speed_70m,wind_direction_70m --forecast-days 3
```

Bash 当前会话（隐藏输入）：

```bash
read -rsp 'GaleWeather API Key: ' GALEWEATHER_API_KEY
export GALEWEATHER_API_KEY
python3 skills/galeweather/scripts/weather.py variables
```

脚本默认请求 `https://www.galeweather.cn/api/v1/weather`，HTTPS上线情况尚未验证。原接口文档地址为HTTP。若暂时只能使用HTTP，知悉Key会明文传输后，由用户显式设置：

```powershell
$env:GALEWEATHER_BASE_URL = 'http://www.galeweather.cn/api/v1/weather'
$env:GALEWEATHER_ALLOW_HTTP = '1'
```

生产发布前推荐服务端启用HTTPS。自定义BASE_URL必须指向可信服务，它将收到授权Header。客户端禁止跟随重定向并保持TLS证书校验。

## 使用示例

向AI提出：“用疾风气象查询纬度36.67、经度117.02未来3天70米风速和风向。”

```bash
python skills/galeweather/scripts/weather.py current --latitude 36.67 --longitude 117.02 --variables temperature_2m,relative_humidity_2m
python skills/galeweather/scripts/weather.py history --latitude 36.67 --longitude 117.02 --variables shortwave_radiation,diffuse_radiation --start-date 2026-07-01 --end-date 2026-07-10 --output history.json
```

成功输出原始JSON；失败向stderr输出不包含凭据的错误并退出1。不会自动重试，不覆盖现有输出。默认超时60秒，可用 `--timeout` 调整至最多300秒。单次响应上限64MiB，长历史请缩短日期范围。要素清单不是线上可用性承诺，优先查询variables辅助接口。

## GitHub发布

建议仓库名 `galeweather-skill`。新建空仓库后，在本目录执行（替换你的GitHub用户名）：

```bash
git init -b main
git add .
git commit -m "Initial GaleWeather skill"
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/galeweather-skill.git
git push -u origin main
```

压缩包含Git bundle备份，可选使用 `git clone galeweather-skill.bundle galeweather-skill` 恢复已提交版本，然后设置远端并推送。不要同时使用两种初始化方式。

发布前确认：服务端路径已实现、HTTPS已开通、variables是否上线、要素实际权限，以及授权Key申请渠道。当前已完成离线测试；未使用真实Key进行线上验证，未替你发布GitHub。仓库没有默认附加开源许可证，请由权利人选定代码许可；气象数据使用权另按服务授权约定。

## 验证

```bash
python -m unittest discover -s tests -v
```

鉴权必须由服务端强制执行：有效期、启停状态、接口权限、配额和坐标授权不能仅依赖客户端判断。客户端代码公开后仍不应允许无Key获取数据。
