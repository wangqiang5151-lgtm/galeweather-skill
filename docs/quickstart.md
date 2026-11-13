# 快速开始与安装

## 1. 获取项目

安装 Python 3.10 或以上版本。可在 GitHub 选择 Code → Download ZIP 并解压；也可使用 Git：

```bash
git clone https://github.com/wangqiang5151-lgtm/galeweather-skill.git
cd galeweather-skill
python --version
```

以下命令均在包含 README.md 的仓库根目录执行。Linux/macOS 如无 python 命令，请使用 python3。无需 pip 安装第三方依赖。

## 2. 申请并配置授权

先确认[试用授权范围](trial-and-quota.md)。环境变量仅对当前终端及其子进程有效；新终端需重新设置。

Windows PowerShell（密码框输入，不要把 Key 写入命令文本）：

```powershell
$credential = Get-Credential -UserName api -Message '在密码框输入疾风气象 API Key'
$env:GALEWEATHER_API_KEY = $credential.GetNetworkCredential().Password
Remove-Variable credential
```

Bash（隐藏输入）：

```bash
read -rsp 'GaleWeather API Key: ' GALEWEATHER_API_KEY
export GALEWEATHER_API_KEY
printf '\n'
```

.env.example 仅是变量说明，脚本不会自动加载 .env。不要提交真实 Key。

默认基础地址为 https://www.galeweather.cn/api/v1/weather，尚未由本项目完成线上核验。若服务方提供其他正式地址，只将可信基础地址填入 GALEWEATHER_BASE_URL，不要附加 /forecast、查询串或 Key。

脚本保持 TLS 证书校验且不跟随重定向。若服务方确认只能使用 HTTP，明文传输风险需由用户知悉并显式配置：

```powershell
$env:GALEWEATHER_BASE_URL = 'http://www.galeweather.cn/api/v1/weather'
$env:GALEWEATHER_ALLOW_HTTP = '1'
```

Bash 对应使用 export GALEWEATHER_BASE_URL='http://www.galeweather.cn/api/v1/weather' 和 export GALEWEATHER_ALLOW_HTTP=1。不要自动降级 HTTP 或关闭证书验证。

## 3. 第一次调用

```bash
python skills/galeweather/scripts/weather.py forecast --latitude 36.67 --longitude 117.02 --variables wind_speed_70m,wind_direction_70m --forecast-days 1 --output wind_forecast.json
```

示例坐标不是自动授权站点，请替换成已授权的坐标。70 米字段也需具有权限。成功时生成 JSON 文件；再次运行请更换文件名，脚本不会覆盖。输出父目录须事先存在。

检查 code 是否为 0、data.records 是否含所需字段，以及时间范围、单位和缺测情况。退出 0 只表示客户端接受响应，不能代替业务数据质量验收。

查询候选可用要素：

```bash
python skills/galeweather/scripts/weather.py variables
```

该命令也需要 Key，并会访问网络；是否消耗额度待服务方确认。辅助接口未上线时，可离线阅读 references/variables.json（位于 skills/galeweather 下），但不能据此认定字段已开放。

## 4. 安装到 AI 宿主

将 skills/galeweather 整个目录复制到宿主规定的技能目录，保留 scripts 和 references。宿主必须支持文件型 SKILL.md、Python 执行和网络访问；仅上传 GitHub 不会自动安装到各类 AI 产品。

Key 需要配置到实际执行 Python 的进程环境中。宿主未继承终端变量时，按其配置说明设置，不要在对话中粘贴 Key。仓库尚未提供已验证的具体宿主版本和默认安装路径。

示例提问：“查询纬度36.67、经度117.02未来一天70米风速和风向。”检查宿主确实调用脚本，并根据真实响应回答。

## 5. 升级

Git 用户在确认没有本地改动后使用 git pull --ff-only；ZIP 用户重新下载并替换客户端。保留本机凭据配置和业务结果，不将它们提交到仓库。API 服务端部署不属于本仓库安装范围。

更多示例见 [examples](../examples/README.md)，失败时见[错误排查](errors.md)。
