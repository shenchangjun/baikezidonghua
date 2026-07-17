# 《Appium App 自动化》使用分享


## 一、环境准备

### 1.1 安装 Node.js（Appium Server 依赖）

Appium 2.x 是 Node 包，先装 Node.js（含 npm）。

- 下载：https://nodejs.org/  选 LTS 版本（如 20.x）
- 安装时一路下一步，勾选「Add to PATH」

验证：

```bash
node -v
npm -v
```

```text
v20.11.1
10.2.4
```

### 1.2 安装 Appium 2.x Server

```bash
npm install -g appium
```

验证：

```bash
appium -v
```

```text
2.5.4
```

### 1.3 安装 Appium 驱动（Android 用 UiAutomator2）

Appium 2.x 驱动需单独装：

```bash
appium driver install uiautomator2
```

验证已装驱动：

```bash
appium driver list --installed
```

```text
✓ uiautomator2 [installed (latest)]
```

> 没有这行说明驱动没装上，重试上一条命令，确认网络可访问 npm。

### 1.4 安装 Python 客户端

```bash
pip install Appium-Python-Client
```

验证：

```bash
python -c "import appium; print(appium.__version__)"
```

```text
3.1.0
```

### 1.5 安装 Appium Inspector（元素定位必备 GUI）

定位元素要用 Inspector 这个独立工具，不是 Server 自带的。

- 下载：https://github.com/appium/appium-inspector/releases
- 选 `Appium-Inspector-windows.zip`，解压运行

界面打开后长这样（示意）：

```
┌─ Appium Inspector（示意）──────────────────────────────┐
│ Remote Host: 127.0.0.1   Port: 4723   Path: /         │
│ ┌─ Capabilities (JSON) ─────────────────────────────┐ │
│ │ {                                                 │ │
│ │   "platformName": "Android",  ← 红框:填 Android   │ │
│ │   "appium:automationName": "UiAutomator2",        │ │
│ │   "appium:deviceName": "emulator-5554",           │ │
│ │   "appium:appPackage": "com.android.settings"     │ │
│ │ }                                                 │ │
│ └───────────────────────────────────────────────────┘ │
│ [ Start Session ]   ← 红框:点这里连接设备            │
└──────────────────────────────────────────────────────┘
```

### 1.6 启动 Server 并确认端口

新开一个命令行，启动 Appium Server（保持这个窗口一直开着）：

```bash
appium
```

```text
[Appium] Welcome to Appium v2.5.4
[Appium] Appium REST http interface listener started on http://0.0.0.0:4723
```

看到 `listener started on ... :4723` 即就绪。Server 默认端口 **4723**。

```
┌─ 终端（示意）──────────────────────────────────────────┐
│ > appium                                              │
│ [Appium] Welcome to Appium v2.5.4                     │
│ [Appium] Appium REST http interface listener          │
│           started on http://0.0.0.0:4723   ← 红框     │
│ （窗口保持打开，不要关）                               │
└──────────────────────────────────────────────────────┘
```

---

## 二、核心功能演示

### 2.1 功能一：desired_caps 配置（连接设备的关键参数）

`desired_caps` 是一组「我想要连接什么样的设备 / App」的参数，发往 Server 建立会话。

最小可用配置（Python）：

```python
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By

options = UiAutomator2Options()
options.platform_name = "Android"
options.automation_name = "UiAutomator2"
options.device_name = "emulator-5554"          # adb devices 看到的序列号
options.app_package = "com.android.settings"   # 要启动的包名
options.app_activity = ".Settings"             # 启动的 Activity

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
print("会话已建立:", driver.session_id)
```

运行后输出：

```text
会话已建立: 3a1b2c...（一串 session id）
```

同时手机/模拟器会自动打开「设置」App。

常用参数速查：

| 参数 | 含义 | 示例 |
|------|------|------|
| `platform_name` | 平台 | `Android` / `iOS` |
| `automation_name` | 自动化引擎 | `UiAutomator2` |
| `device_name` | 设备名/序列号 | `emulator-5554` |
| `app_package` | 应用包名 | `com.android.settings` |
| `app_activity` | 启动 Activity | `.Settings` |
| `app` | 本地 APK 路径（首次装） | `C:\app.apk` |
| `no_reset` | 不清除应用数据 | `True` |
| `new_command_timeout` | 无命令超时(秒) | `300` |

> 找不到 `app_activity`？用 ADB：`adb shell dumpsys window | findstr mCurrentFocus` 看当前 Activity。

### 2.2 功能二：元素定位（找到你要点的那个控件）

先启动 Inspector（`appium` Server 已开 → 打开 Appium Inspector → 填 1.5 的 capabilities → 点 Start Session）。连接成功后界面：

```
┌─ Appium Inspector 连接后（示意）──────────────────────┐
│ [ 截图区: 手机画面 ]      [ Selected Element 面板 ]     │
│  ┌────────────┐          resource-id:                 │
│  │   WLAN     │  ←点   │  android:id/title             │
│  │   蓝牙     │          text: WLAN                    │
│  │   显示     │          class: android.widget.TextView│
│  └────────────┘          xpath: //*[@text="WLAN"] ←红框│
│  [ Tap ] [ Swipe ] [ Find ]                            │
└──────────────────────────────────────────────────────┘
```

在左侧点屏幕上的「WLAN」，右侧出现它的属性。常用定位方式（Python）：

```python
from selenium.webdriver.common.by import By

# 1) 按 id（最稳，优先用）
wlan = driver.find_element(By.ID, "android:id/title")

# 2) 按 text（UiAutomator 专属，好用）
wlan = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("WLAN")')

# 3) 按 xpath（最慢，万不得已才用）
wlan = driver.find_element(By.XPATH, '//*[@text="WLAN"]')

# 4) 多种条件组合
btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.Button").text("确定")')
```

`AppiumBy` 需导入：

```python
from appium.webdriver.common.appiumby import AppiumBy
```

定位方式对比与建议：

| 方式 | 稳定性 | 速度 | 建议 |
|------|--------|------|------|
| ID (`resource-id`) | ★★★★★ | 快 | 首选 |
| UiSelector (text/class) | ★★★★ | 中 | 次选 |
| XPath | ★★★ | 慢 | 兜底 |

### 2.3 功能三：手势操作（点击 / 输入 / 滑动 / 长按）

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.pointer_input import PointerInput
import time

# 点击
driver.find_element(By.XPATH, '//*[@text="WLAN"]').click()

# 输入文本（需控件获得焦点，如搜索框）
search = driver.find_element(By.ID, "android:id/search_src_text")
search.send_keys("hello")

# 滑动（从下往上滑，常用于列表翻页）
size = driver.get_window_size()
w, h = size["width"], size["height"]
driver.swipe(w//2, h*0.8, w//2, h*0.2, 800)   # 起点→终点, 800ms

# 长按（用 W3C actions）
def long_press(x, y, ms=2000):
    driver.tap([(x, y)], ms)

long_press(200, 400)
time.sleep(1)
```

滑动参数说明：`swipe(start_x, start_y, end_x, end_y, duration_ms)`。

复杂手势（双指缩放等）用 `ActionBuilder` + `PointerInput`，但日常 90% 场景用 `click / send_keys / swipe / tap` 足够。

### 2.4 功能四：等待机制（自动化稳定的核心）

**不要**用 `time.sleep(3)` 硬等——慢且不可靠。用显式等待：

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)   # 最多等 10 秒

# 等元素出现并可点击，再操作
el = wait.until(
    EC.element_to_be_clickable((By.XPATH, '//*[@text="WLAN"]'))
)
el.click()
```

常用等待条件：

| 条件 | 含义 |
|------|------|
| `presence_of_element_located` | 元素出现在 DOM |
| `element_to_be_clickable` | 元素可见且可点 |
| `visibility_of_element_located` | 元素可见 |
| `invisibility_of_element_located` | 元素消失（等加载圈消失） |
| `text_to_be_present_in_element` | 文本出现（等登录成功提示） |

三种等待区别：

| 等待 | 行为 | 建议 |
|------|------|------|
| 硬性 `time.sleep` | 无条件等固定秒数 | 禁用 |
| 隐式 `driver.implicitly_wait(10)` | 全局找元素超时 | 可设但别和显式混用 |
| 显式 `WebDriverWait` | 等特定条件成立 | 首选 |

> 隐式 + 显式混用会让超时时间叠加成乘法关系，坑很多，**只用显式等待**。

---

## 三、实战示例

用一个完整脚本串起所有功能：**自动打开设置 → 进入 WLAN → 等待列表加载 → 滑动查看 → 断言标题存在**。

### 3.1 项目背景

回归测试「设置」App 的 WLAN 入口是否能正常进入并展示网络列表。脚本自动完成，省去人工点检。

### 3.2 完整代码

```python
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. desired_caps 配置
options = UiAutomator2Options()
options.platform_name = "Android"
options.automation_name = "UiAutomator2"
options.device_name = "emulator-5554"
options.app_package = "com.android.settings"
options.app_activity = ".Settings"
options.no_reset = True

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
wait = WebDriverWait(driver, 10)

# 2. 元素定位 + 显式等待，点击 WLAN
wlan = wait.until(EC.element_to_be_clickable(
    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("WLAN")')))
wlan.click()

# 3. 等待 WLAN 页面标题出现（等待机制）
title = wait.until(EC.presence_of_element_located(
    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("WLAN")')))
print("已进入 WLAN 页面，标题:", title.text)

# 4. 手势：上滑查看网络列表
size = driver.get_window_size()
driver.swipe(size["width"]//2, int(size["height"]*0.8),
             size["width"]//2, int(size["height"]*0.2), 800)

# 5. 断言列表非空（用 find_elements 找多个）
networks = driver.find_elements(
    AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.TextView")')
print("可见文本控件数量:", len(networks))
assert len(networks) > 0, "WLAN 页面没有加载出任何内容"

print("✅ 自动化用例通过")
driver.quit()
```

### 3.3 运行结果

先在另一个窗口启动 Server：`appium`（保持打开）。然后运行脚本：

```bash
python wlan_test.py
```

```text
已进入 WLAN 页面，标题: WLAN
可见文本控件数量: 12
✅ 自动化用例通过
```

```
┌─ 运行结果（示意）──────────────────────────────────────┐
│ > python wlan_test.py                                  │
│ 已进入 WLAN 页面，标题: WLAN                            │
│ 可见文本控件数量: 12                                    │
│ ✅ 自动化用例通过          ← 红框:看到这行即跑通        │
└──────────────────────────────────────────────────────┘
```

手机上会实际发生：打开设置 → 点 WLAN → 滑一下。全流程无需人工干预。

---

## 四、踩坑记录

### 坑 1：报 `A new session could not be created ... UiAutomator2 is not installed`

**现象**：建立会话失败，提示驱动未安装。
**解决**：Server 端装驱动（见 1.3）：

```bash
appium driver install uiautomator2
```

### 坑 2：报 `Could not find a connected Android device`

**现象**：连不上设备。
**原因**：`adb devices` 里设备是 `unauthorized` 或 `offline`。
**解决**：手机点允许；或 `adb kill-server && adb start-server` 后重插线。先确保 `adb devices` 正常再跑脚本。

### 坑 3：报 `An element could not be located ... using: AppiumBy.XPATH`

**现象**：定位不到元素。
**排查**：用 Appium Inspector 的「Find」功能贴同样的表达式试。常见原因：
- 页面还没加载完 → 加显式等待，别用 sleep
- 元素在 WebView/弹窗里 → 需切换 context（`driver.switch_to.context(...)`）
- id 写成 `android:id/title` 但缺 `appium:` 前缀无关，ID 直接写全即可

### 坑 4：启动报 `Activity used to start app doesn't exist`

**现象**：`app_activity` 填错。
**解决**：用 ADB 查真实 Activity：

```bash
adb shell dumpsys window | findstr mCurrentFocus
```

输出形如 `mCurrentFocus=... com.android.settings/.Settings`，取 `/` 后的部分。

### 坑 5：脚本跑着跑着卡住不动

**现象**：长时间无响应。
**原因**：`new_command_timeout`（默认 60s）内没发新命令，Server 杀掉会话。
**解决**：初始化时加大超时：

```python
options.new_command_timeout = 300
```

### 坑 6：隐式 + 显式等待混用导致等待时间异常长

**现象**：一个元素等了远超 10 秒。
**原因**：两者超时相乘。
**解决**：删掉 `driver.implicitly_wait(...)`，统一用显式 `WebDriverWait`。

### 坑 7：中文输入变成乱码或不生效

**现象**：`send_keys("你好")` 输不进去。
**解决**：capabilities 加：

```python
options.unicode_keyboard = True
options.reset_keyboard = True
```

---

## 五、总结

### 优点

- 跨平台（Android/iOS 同一套 API）、开源免费
- 基于 WebDriver 标准协议，Python/Java 客户端齐全，文档多
- 无需改 App 源码即可自动化（黑盒）
- Appium Inspector 可视化定位，降低上手门槛

### 缺点

- 环境搭建步骤多（Node + Server + 驱动 + 客户端），新人易卡在环境
- 启动会话慢（每次要推 UiAutomator2 Server 到设备）
- 控件属性不稳定（resource-id 缺失、动态 text）时维护成本高
- 不支持系统级弹窗（如权限弹窗）的稳定处理，常需额外封装

### 适用场景

- App 回归测试、冒烟测试自动化
- 重复性手测操作（批量装机验证、表单填写）
- 兼容性矩阵测试（多机型跑同一脚本）
- 不适合：强动画/游戏渲染类、需 root 的系统层操作

---

### 命令 / 代码速查表

| 功能 | 写法 |
|------|------|
| 装 Server | `npm install -g appium` |
| 装驱动 | `appium driver install uiautomator2` |
| 启 Server | `appium`（端口 4723） |
| 建会话 | `webdriver.Remote("http://127.0.0.1:4723", options)` |
| 按 ID 定位 | `find_element(AppiumBy.ID, "android:id/title")` |
| 按 text 定位 | `find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("WLAN")')` |
| 显式等待 | `WebDriverWait(driver,10).until(EC.element_to_be_clickable(...))` |
| 滑动 | `driver.swipe(x1,y1,x2,y2,800)` |
| 点击 | `el.click()` |
| 输入 | `el.send_keys("文本")` |
| 退出 | `driver.quit()` |
