# 《AutoUI AI 驱动测试》使用分享

> 面向人群：会 ADB、想用「说人话」的方式驱动手机自动化的测试同学。
> 配套前置：《ADB 调试工具使用分享》——AutoUI 底层依赖 ADB 连设备，请先确保 `adb devices` 能看到设备。
> 本文只讲实操，跟着做就能连上手机、用一句话跑通自动化、并自己写一个 Skill。所有「截图」用 GUI 布局 / 日志 ASCII 框代替，框内（红框标注）处是你要看的关键信息。资料来源：Sun-AutoUI v260506 官方使用手册 + Skill 开发手册（更新日期 2026-05-06）。

---

## 一、环境准备

### 1.1 环境与要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10 / 11 |
| Android 设备 | 真机或模拟器（需启用 USB 调试）|
| ADB | 系统已安装（见 ADB 文档 1.1~1.3）|
| 视觉语言模型 | 兼容 OpenAI API 的 VL 模型（如 AutoGLM-Phone 系列）|
| Python | 3.10+（仅运行源码时需要；用 exe 版不需）|

### 1.2 连接手机

**USB 方式**

手机：设置 → 开发者选项 → USB 调试 → 开启。插线后在电脑确认：

```bash
adb devices
```

```text
List of devices attached
8AHX1LPHC1745	device
```

**WiFi 方式**

手机：设置 → 开发者选项 → 无线调试 → 开启。然后：

```bash
adb connect 192.168.1.100:5555
adb devices
```

```text
List of devices attached
192.168.1.100:5555	device
```

### 1.3 启动程序并配置模型

双击运行 `sun-AutoUI260506.exe`。

在 GUI **左侧配置区**填写模型信息：

| 参数 | 说明 | 示例 |
|------|------|------|
| Base URL | 模型 API 地址 | `http://localhost:8000/v1` |
| Model Name | 模型名称 | `autoglm-phone-9b` |
| API Key | API 密钥 | `EMPTY` |

```
┌─ GUI 配置区（示意）──────────────────────────────────┐
│ 模型配置                                              │
│ Base URL:  http://localhost:8000/v1    ← 红框        │
│ Model Name: autoglm-phone-9b           ← 红框        │
│ API Key:    EMPTY                                     │
│ Agent: Max Steps 100 | Language cn                   │
│ 设备: Device ID 自动检测                              │
└──────────────────────────────────────────────────────┘
```

> Agent 配置：`Max Steps` 默认 100（任务太复杂跑不完就调大）；`Language` 默认 `cn`。设备默认自动检测。

---

## 二、核心功能演示

### 2.1 功能一：GUI 界面（认识四个区域）

启动后主界面布局：

```
┌─────────────────────────────────────────────────────┐
│  ☀️ Sun-AutoUI - AI驱动的Android自动化测试平台       │
├──────────┬──────────────────────────────────────────┤
│  配置区  │          任务对话区                        │
│  - 模型  │  ┌────────────────────────────────────┐  │
│  - Agent │  │ 用户: 打开微信并搜索公众号           │  │
│  - 设备  │  │ AI: 正在执行任务...                 │  │
│          │  │ AI: 任务完成                        │  │
│  [🚀发送] │  └────────────────────────────────────┘  │
│  [⏹️终止] │                                        │
├──────────┴──────────────────────────────────────────┤
│  思考执行过程（日志区）                               │
│  [Thinking] 思考:...                                 │
│  [Action] 操作: do(action="Launch", app="微信")      │
├─────────────────────────────────────────────────────┤
│  执行结果: 任务已成功完成                             │
└─────────────────────────────────────────────────────┘
```

**四个区域职责**

| 区域 | 作用 |
|------|------|
| 配置区（左）| 填模型 / Agent / 设备参数 |
| 任务对话区（右）| 输入任务描述，点 🚀 发送 |
| 思考执行过程（日志区）| 看 [Thinking] 思考、[Action] 操作、[DONE] |
| 执行结果（底部）| 最终成功/失败结论 |

**按钮功能**

| 按钮 | 功能 |
|------|------|
| 🚀 发送 | 开始执行任务 |
| ⏹️ 终止任务 | 优雅停止（下一步检查时退出）|
| 🔄 清空对话 | 清任务对话区 |
| 📋 清空日志 | 清执行过程区 |

### 2.2 功能二：手机自动化（用一句话驱动）

不用写代码，直接在任务对话区输入自然语言。

**示例 1：简单任务**

输入任务：

```text
打开sun记账本
```

执行日志：

```text
[Thinking] 用户要求打开sun记账本应用...
[Action] do(action="Launch", app="sun记账本")
[Action] do(action="Wait", duration="2 seconds")
[DONE] 任务已完成
```

执行结果：`任务执行成功：应用已成功打开`

**示例 2：复合任务**

输入任务：

```text
打开微信并搜索公众号Python
```

执行流程：打开微信 → 点击搜索 → 输入"Python" → 查看结果 → 任务完成。

**支持的操作类型**

| 操作 | 说明 | 示例任务 |
|------|------|----------|
| 打开应用 | 启动指定应用 | "打开微信" |
| 点击 | 点屏幕位置 | "点击登录按钮" |
| 输入文字 | 输入框输入 | "输入用户名admin" |
| 滑动 | 上下左右滑 | "向下滑动查看更多" |
| 返回 | 回上一级 | "返回上一页" |
| 主页 | 回桌面 | "回到桌面" |
| 等待 | 等页面加载 | "等待3秒" |

### 2.3 功能三：Skill 开发（零代码扩展能力）

Skill 是 `.md` 文档，告诉 AI 在特定关键词下按固定步骤执行。放在：

```
~/.sun-autoui/skills/        # 即 C:\Users\你的用户名\.sun-autoui\skills\
├── open_app_and_search.md
├── send_dingtalk_notification.md
└── your_skill.md
```

**创建一个 Skill（微信搜索）**

```bat
@rem Windows 打开目录创建文件
notepad %USERPROFILE%\.sun-autoui\skills\my_first_skill.md
```

文件内容：

```markdown
# 打开微信并搜索

## 触发条件
当用户提到以下关键词时激活：
- "微信搜索"
- "打开微信搜索"
- "在微信搜索"

## 操作步骤

1. 打开微信应用
   ```
   do(action="Launch", app="微信")
   ```

2. 点击搜索框
   ```
   do(action="Tap", element=[900, 100])
   ```

3. 输入搜索内容
   ```
   do(action="Type", text="搜索关键词")
   ```

## 示例

**示例1**: 搜索公众号
用户: "在微信搜索公众号Python"
→ 打开微信 → 点击搜索 → 输入"Python" → 查看结果
```

**关键结构（四段式）**

| 段落 | 作用 | 规范 |
|------|------|------|
| `# 标题` | Skill 名称 | 简洁、无特殊字符 |
| `## 触发条件` | 激活关键词 | 多个同义词、用引号、2~6 字 |
| `## 操作步骤` | 有序列表 + action 代码块 | 每步先文字后代码 |
| `## 示例` | 2~3 个真实场景 | `用户:` + `→` 流程 |

**支持的 Actions（写进代码块）**

UI 操作：

| Action | 参数 | 示例 |
|--------|------|------|
| Launch | app | `do(action="Launch", app="微信")` |
| Tap | element | `do(action="Tap", element=[500, 800])` |
| Type | text | `do(action="Type", text="搜索内容")` |
| Swipe | start, end | `do(action="Swipe", start=[500,800], end=[500,200])` |
| Back | - | `do(action="Back")` |
| Home | - | `do(action="Home")` |
| Wait | duration | `do(action="Wait", duration="2 seconds")` |
| Double Tap | element | `do(action="Double Tap", element=[500,800])` |
| Long Press | element | `do(action="Long Press", element=[500,800])` |

高级操作：

| Action | 参数 | 示例 |
|--------|------|------|
| Call_API | url, method, headers, payload | 发送 HTTP 请求 |
| Save_Screenshot | filename | `do(action="Save_Screenshot", filename="s.png")` |
| Take_over | message | `do(action="Take_over", message="请手动操作")` |
| Note | message | `do(action="Note", message="True")` |
| Get_Clipboard | - | 获取剪贴板 |
| Set_Clipboard | text | 设置剪贴板 |
| finish | message | `finish(message="任务完成说明")` |

> ⚠️ `element=[x, y]` 是屏幕坐标，需按设备分辨率调整。获取方法见 2.4 / 第四章。

**重启 GUI 加载 Skill**

关闭并重新打开 `sun-AutoUI260506.exe`，观察启动日志确认加载：

```text
📦 Skills System
✅ Loaded 2 skill(s) from:
   C:\Users\用户名\.sun-autoui\skills

📋 Available Skills:
   • 打开应用并搜索
     触发: 打开, 启动, 搜索
```

**验证匹配**

在任务对话区输入：

```text
在微信搜索公众号Python
```

日志区应显示：

```text
🎯 检测到 1 个匹配的Skill:
   • 打开微信并搜索
     触发词: 微信搜索
```

### 2.4 功能四：任务配置 + 接口测试 / 钉钉推送

**任务配置项**

| 类别 | 参数 | 默认 | 说明 |
|------|------|------|------|
| Agent | Max Steps | 100 | 任务太复杂跑不完就调大 |
| Agent | Language | cn | 语言 |
| 设备 | Device ID | 自动检测 | 多设备时可指定 |

**接口测试（Call_API）**

Skill 里用 `Call_API` 发 HTTP 请求。示例：API 健康检查 + 钉钉报告（消息必须含「报告」关键字）：

```markdown
## 操作步骤

1. 发送 GET 请求检查 API
   ```
   do(action="Call_API",
      url="https://api.example.com/health",
      method="GET",
      headers={"Content-Type": "application/json"})
   ```

2. 发送钉钉报告
   ```
   do(action="Call_API",
      url="https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
      method="POST",
      headers={"Content-Type": "application/json"},
      payload={
        "msgtype": "markdown",
        "markdown": {
          "title": "API健康检查报告",
          "text": "## 📊 API健康检查报告\n\n**状态**: ✅ 正常"
        }
      })
   ```

3. 完成任务
   ```
   finish(message="API健康检查完成，已发送报告")
   ```
```

**钉钉推送（内置 Skill）**

内置 `send_dingtalk_notification.md`，触发词含「发送钉钉通知」。直接在任务里加一句即可：

```text
打开sun记账本，测试跳过登录功能，然后把刚才的测试结果发送钉钉通知
```

日志会显示：先跑手机操作，Skill 自动接管发钉钉：

```text
🎯 检测到程序化Skill: 发送钉钉通知
📤 执行程序化Skill: 发送钉钉通知
✅ API call successful
```

钉钉群收到 Markdown 报告卡片（含执行摘要、✅/❌ 状态）。

**UI + API 联合测试**

先 UI 操作（如添加一笔账），再 `Call_API` 拉数据对比，最后发报告——案例详见官方手册案例 3。

---

## 三、实战示例

用一个完整 Skill 串起各功能：**写「测试跳过登录」Skill → 加载 → 一句话触发 → 自动跑 UI 测试 + 钉钉报告**。

### 3.1 项目背景

回归测试「sun 记账本」的跳过登录功能，并用钉钉通知结果，全程不写一行 Python。

### 3.2 完整操作流程

**第 1 步：写 Skill 文件** `C:\Users\你的用户名\.sun-autoui\skills\test_login_skip.md`

```markdown
# 测试跳过登录功能

## 触发条件
当用户提到以下关键词时激活：
- "测试跳过登录"
- "跳过登录"
- "测试登录"
- "测试sun记账本"

## 操作步骤

1. 打开sun记账本应用
   ```
   do(action="Launch", app="sun记账本")
   ```

2. 等待应用加载
   ```
   do(action="Wait", duration="2 seconds")
   ```

3. 点击跳过登录按钮
   ```
   do(action="Tap", element=[499, 921])
   ```

4. 等待进入首页
   ```
   do(action="Wait", duration="1 seconds")
   ```

5. 验证是否成功进入首页
   - 检查是否显示"Sun 记账本"标题
   - 检查是否显示"游客模式已登录"提示

6. 完成任务
   ```
   finish(message="跳过登录功能测试成功，已进入游客模式")
   ```

## 示例

**示例1**: 测试跳过登录
用户: "测试sun记账本的跳过登录功能"
→ 打开应用 → 检测登录界面 → 点击跳过登录 → 验证进入首页
```

**第 2 步：重启 GUI，确认加载**

启动日志出现 `✅ Loaded ... test_login_skip`。

**第 3 步：输入任务并发送**

```text
测试sun记账本的跳过登录功能，发送钉钉通知
```

**第 4 步：看日志与结果**

```text
[Thinking] 用户要求测试跳过登录功能...
[Action] do(action="Launch", app="sun记账本")
[Action] do(action="Tap", element=[499, 921])
[DONE] 任务已完成
📤 执行程序化Skill: 发送钉钉通知
✅ API call successful
```

### 3.3 最终结果

```
┌─ 执行结果（示意）──────────────────────────────────────┐
│ 任务已成功完成              ← 红框                    │
│ 钉钉群收到: ## 📱 Sun-AutoUI自动化报告                │
│   **状态**: ✅ 成功   ← 红框                          │
│   1. 打开 sun记账本 ✓  2. 点击跳过登录 ✓             │
└──────────────────────────────────────────────────────┘
```

---

## 四、踩坑记录

### 坑 1：GUI 没检测到 Skill

**现象**：输入任务没触发自定义 Skill。
**排查**：文件是否在 `~/.sun-autoui/skills/`；扩展名是否 `.md`；改完**必须重启 GUI**（见 2.3）。启动日志应出现 `✅ Loaded N skill(s)`。

### 坑 2：Skill 没匹配到

**现象**：日志无 `🎯 检测到匹配的Skill`。
**解决**：触发词要用引号包、2~6 字、提供多个同义词；用户任务里要包含其中一个词。看日志 `触发词:` 行确认。

### 坑 3：坐标点歪 / 点不到元素

**现象**：`Tap` 点错位置。
**原因**：`element=[x,y]` 是绝对像素，分辨率不同坐标不同。
**获取坐标**：
- ADB：`adb shell dumpsys window | findstr "mFocusedApp"`
- GUI 截图后目测记录坐标
- 用相对坐标（如屏幕中部偏右 `[800, 500]`）
> 应用更新布局后需同步更新 Skill 坐标。

### 坑 4：任务跑到一半卡住 / 没跑完

**现象**：日志停在中间不再动。
**解决**：在配置区调大 `Max Steps`（默认 100）；检查模型 API 是否可用；必要时点 ⏹️ 终止任务重跑。

### 坑 5：钉钉没收到通知

**现象**：任务成功但群里无消息。
**排查**：
- 任务里是否含「发送钉钉通知」类触发词（或显式 Call_API）
- Webhook `access_token` 是否替换成真实值
- 钉钉消息 **必须含「报告」关键字**，否则被拒
- 网络能否访问 `oapi.dingtalk.com`

### 坑 6：接口调用失败

**现象**：`Call_API` 报错。
**排查**：URL 是否正确、网络通不通、请求参数格式（尤其 JSON payload 引号）、响应错误信息。

### 坑 7：模型连不上 / 思考为空

**现象**：发送后无 [Thinking]。
**解决**：检查左侧 `Base URL` / `Model Name` / `API Key`；确认模型服务已启动且兼容 OpenAI API（如 `autoglm-phone-9b`）。

### 坑 8：弹窗打断流程

**现象**：中途跳出权限/广告弹窗导致步骤错位。
**解决**：Skill 里加容错——「如果遇到弹窗，先关闭或返回再继续」；必要时用 `Take_over` 请求人工接管。

---

## 五、总结

### 优点

- 零代码：用自然语言 + Markdown Skill 驱动，测试人员无需写 Python
- AI 视觉驱动：理解屏幕内容智能决策，不依赖元素 id（对比 Appium 需定位）
- 能力完整：UI 自动化 + 接口测试（Call_API）+ 钉钉报告一体
- Skill 可复用、版本控制友好（纯 .md），系统自动匹配注入
- 友好 GUI，无需命令行操作

### 缺点

- 依赖视觉语言模型可用性（需自备兼容 OpenAI API 的 VL 模型）
- 坐标式 `Tap` 受分辨率/布局变化影响，需维护
- 任务执行步数受 Max Steps 限制，超复杂链路要调参
- 自研平台（v260506），依赖官方维护与文档

### 适用场景

- 手机 App 功能回归（用一句话描述任务，AI 自动跑）
- 跳过登录、表单填写等固定流程的 Skill 化沉淀
- UI 操作 + 接口校验的端到端联合测试
- 测试结果自动钉钉推送，团队实时感知
- 不适合：强断言精度、需元素级稳定定位的用例（那用 Appium）

---

### 速查表

| 功能 | 写法 |
|------|------|
| 连设备 | `adb devices` / `adb connect IP:5555` |
| 启动 | 双击 `sun-AutoUI260506.exe` |
| 模型配置 | 左侧 Base URL / Model Name / API Key |
| 发任务 | 任务对话区输入 → 🚀 发送 |
| 终止 | ⏹️ 终止任务 |
| Skill 目录 | `%USERPROFILE%\.sun-autoui\skills\` |
| Skill 结构 | `# 标题` / `## 触发条件` / `## 操作步骤` / `## 示例` |
| 打开应用 | `do(action="Launch", app="微信")` |
| 点击 | `do(action="Tap", element=[500,800])` |
| 输入 | `do(action="Type", text="内容")` |
| 等待 | `do(action="Wait", duration="2 seconds")` |
| 调接口 | `do(action="Call_API", url=..., method="POST", ...)` |
| 结束 | `finish(message="说明")` |
| 钉钉 | 任务加「发送钉钉通知」（消息须含「报告」）|
| 验证加载 | 启动日志 `✅ Loaded N skill(s)` |
| 验证匹配 | 任务日志 `🎯 检测到 N 个匹配的Skill` |
