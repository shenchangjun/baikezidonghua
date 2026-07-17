# 《EasyWeb 自研平台》使用分享

> 面向人群：会一点 Python、想用「写数据不写代码」的方式做 Web 自动化的测试同学。
> 配套前置：本文是团队自研平台 EasyWeb v2.0（gitcode 仓库 `sun-EasyWeb`），无需 ADB/Appium，独立可跑。
> 本文只讲实操，跟着做就能跑通第一个用例并看懂 Allure 报告。所有「截图」用终端回显 / 界面 ASCII 框代替，框内（红框标注）处是你要看的关键信息。资料来源：EasyWeb v2.0 官方使用说明（作者：孙文龙）。

---

## 一、环境准备

### 1.1 获取项目

推荐 git clone（仓库含浏览器/驱动等大文件，已用 Git LFS）：

```bash
git clone https://gitcode.com/gcw_OIVuYjdN/sun-EasyWeb.git
cd sun-EasyWeb
```

更新代码：

```bash
git pull origin master
```

### 1.2 安装依赖

- Python 要求：**3.11+**
- 框架版本：**EasyWeb 2.0+**

```bash
pip install -r requirements.txt
```

### 1.3 验证安装

```bash
python main.py --help
```

有参数说明输出即安装成功。

### 1.4 测试网站（无需额外安装）

框架已内置本地测试网站 `pkg/UITestWebsite/UITestWebsite.exe`。

- 自动启动（推荐）：运行 `python main.py` 或双击 `run_tests.bat`，框架自动启停网站
- 手动启动：直接运行 `pkg/UITestWebsite/UITestWebsite.exe`
- 访问地址：**http://localhost:5000** 或 http://127.0.0.1:5000
- 默认端口 5000，可在 `config/settings.yaml` 改 `website_port`
- 关闭自动启动：设 `auto_start_website: false`
- 命令行禁用：`python main.py --no-website`

```
┌─ 浏览器访问测试网站（示意）────────────────────────────┐
│ 地址栏: http://localhost:5000        ← 红框:默认端口    │
│ 页面: EasyWeb 内置 UITestWebsite 首页                  │
└──────────────────────────────────────────────────────┘
```

---

## 二、核心功能演示

### 2.1 功能一：快速上手（一键运行）

**方式一：Windows 双击**

直接双击 `run_tests.bat`。

**方式二：命令行运行**

```bash
python main.py --headless --no-website
```

> 用 `--no-website` 时前提是你已手动启动了测试网站（见 1.4）。首次建议直接 `python main.py` 让它自动启停。

运行成功后控制台输出测试进度，并在 `allure-report/` 生成 HTML 报告。

**CLI 常用参数**

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--config` | `-c` | 指定配置文件 | `python main.py -c config/prod.yaml` |
| `--test` | `-t` | 按类型过滤用例 | `python main.py -t login`（search/login/nav/locator/workflow/all）|
| `--engine` | `-e` | 指定引擎 | `python main.py -e playwright`（selenium/playwright）|
| `--browser` | `-b` | 指定浏览器 | `python main.py -b chromium` |
| `--headless` | - | 无头模式 | `python main.py --headless` |
| `--no-website` | - | 不自动启网站 | `python main.py --no-website` |
| `--no-report` | - | 不生成报告 | `python main.py --no-report` |
| `--open-report` | - | 跑完打开报告（默认开）| `python main.py --open-report` |
| `--data-file` | `-d` | 指定数据文件 | `python main.py -d data/test_data.json` |
| `--cookie` | `-C` | 注入 Cookie（可多次）| `python main.py -C "token=abc123"` |

**常用组合示例**

```bash
# 只跑登录测试，用 Playwright 引擎
python main.py -t login -e playwright

# 指定数据文件，无头模式
python main.py -d data/my_test.json --headless

# 注入 Cookie 绕过登录
python main.py -C "session_id=xyz789" -C "user_role=admin"

# 自定义配置，不生成报告（提速）
python main.py -c config/ci.yaml --no-report
```

```
┌─ 控制台运行输出（示意）────────────────────────────────┐
│ [EasyWeb] 启动测试网站 http://localhost:5000           │
│ [EasyWeb] 加载用例 12 条                                │
│ PASSED  TC001 搜索Selenium                             │
│ PASSED  TC008 元素定位-ID定位                          │
│ 生成 Allure 报告 -> allure-report/index.html ← 红框    │
└──────────────────────────────────────────────────────┘
```

### 2.2 功能二：字段维护（核心——只维护数据，不写代码）

框架采用**统一标准字段**，测试人员只改数据文件（Excel/JSON），不用碰 Python。

**字段说明表**

| 字段名 | 说明 | 示例值 | 必填 |
|--------|------|--------|------|
| `id` | 用例唯一标识 | `TC001` | ✅ |
| `name` | 用例名称 | `搜索Selenium` | ✅ |
| `type` | 用例类型（路由依据）| `search`/`login`/`nav`/`locator` | ✅ |
| `url` | 测试页面地址 | `${base_url}/login` | ✅ |
| `selector` | 元素定位器 | `#username` 或 `首页` | ⭕ |
| `value` | 输入/操作的值 | `admin` 或 `admin,123456` | ⭕ |
| `result_selector` | 结果元素定位器 | `.welcome` | ❌ |
| `expected_type` | 期望结果类型 | `title`/`text`/`url`/`value`/`click` | ✅ |
| `expected_value` | 期望结果内容 | `登录成功` | ✅ |
| `priority` | 优先级 | `P0`/`P1` | ❌ |
| `description` | 用例描述 | `验证管理员登录` | ❌ |

> ⚠️ `config/settings.yaml` 中 `auto_start_website` 必须是布尔值 `true`/`false`（注意拼写）；`base_url` 需与测试网站端口一致（默认 5000）。

**JSON 数据示例**（写进 `data/test_data.json`）

```json
[
    {
        "id": "TC001",
        "name": "搜索Selenium",
        "type": "search",
        "url": "${base_url}/",
        "selector": "#search-input",
        "value": "selenium",
        "expected_type": "title",
        "expected_value": "搜索",
        "priority": "P0",
        "description": "验证首页搜索功能"
    }
]
```

> 💡 占位符 `${base_url}` 自动替换为 `config/settings.yaml` 里的 `base_url` 值。

**Excel 数据示例**（首行是标准字段表头，后续是数据；支持多 Sheet 自动合并）

| id | name | type | url | selector | value | expected_type | expected_value | priority | description |
|----|------|------|-----|----------|-------|---------------|----------------|----------|-------------|
| TC001 | 搜索Selenium | search | ${base_url}/ | #search-input | selenium | title | 搜索 | P0 | 验证搜索功能 |

**Excel vs JSON 怎么选**

| 维度 | Excel (.xlsx) | JSON (.json) |
|------|---------------|--------------|
| 适用人群 | 测试工程师、业务专家 | 自动化工程师、开发 |
| 优势 | 可视化、筛选排序、批量快、无语法错 | 结构化、Git 友好、CI 友好、支持嵌套 |
| 推荐场景 | 日常用例维护、手工转自动化 | 代码集成、复杂数据、CI 流水线 |

> 💡 建议：日常维护用 Excel，代码提交和 CI 用 JSON。底层格式统一，测试代码无需任何修改。

运行指定数据文件：

```bash
python main.py -d data/test_data.json
```

### 2.3 功能三：元素定位（八大方法 + `by` 字段切换）

框架完整支持 Selenium 八大定位方法，通过 `by` 字段灵活切换。

**定位方法对照表**

| 序号 | 定位方法 | `by` 参数值 | 示例 selector | 适用场景 |
|------|----------|-------------|---------------|----------|
| 1 | ID | css（默认）| `#username` | 最稳定，优先用 |
| 2 | Name | css | `[name='email']` | 表单元素 |
| 3 | Class | css | `.password-field` | 多元素共享样式 |
| 4 | Tag | `tag_name` | `input` | 页面唯一标签 |
| 5 | Link Text | `link_text` | `首页` | 完整链接文本 |
| 6 | Partial Link | `partial_link_text` | `联系` | 部分链接文本 |
| 7 | XPath | `xpath` | `//input[@id='x']` | 复杂结构 |
| 8 | CSS | css | `.xpath-class` | 灵活组合 |

**实战用例配置**

① ID 定位（默认 css，`#` 即 id）

```json
{
    "id": "TC008",
    "name": "元素定位-ID定位",
    "type": "locator",
    "url": "${base_url}/elements",
    "selector": "#username",
    "value": "test_user",
    "expected_type": "value",
    "expected_value": "test_user"
}
```

② Name 定位

```json
{
    "id": "TC009",
    "name": "元素定位-Name定位",
    "type": "locator",
    "url": "${base_url}/elements",
    "selector": "[name='email']",
    "value": "test@example.com",
    "expected_type": "value",
    "expected_value": "test@example.com"
}
```

③ XPath 定位（必须显式写 `"by": "xpath"`）

```json
{
    "id": "TC011",
    "name": "元素定位-XPath定位",
    "type": "locator",
    "url": "${base_url}/elements",
    "selector": "//input[@id='xpath-input']",
    "by": "xpath",
    "value": "xpath_test",
    "expected_type": "value",
    "expected_value": "xpath_test"
}
```

④ Link Text 定位

```json
{
    "id": "TC013",
    "name": "元素定位-LinkText定位",
    "type": "locator",
    "url": "${base_url}/elements",
    "selector": "首页",
    "by": "link_text",
    "expected_type": "click",
    "expected_value": "success"
}
```

> 💡 技巧：优先用 id 和 css；遇到动态 ID 或复杂 DOM 再用 xpath。

### 2.4 功能四：双引擎切换（Selenium / Playwright）

框架支持配置一键切换底层引擎，**测试代码和数据完全不用改**。

**切换方法**：编辑 `config/settings.yaml`

```yaml
# 使用 Selenium（默认）
engine: selenium
browser: chrome

# 切换为 Playwright
engine: playwright
browser: chromium
```

**双引擎验证步骤**

1. Selenium 验证：保持默认 `engine: selenium`，运行 `python main.py`，控制台日志显示 `SeleniumEngine`。
2. Playwright 验证：改成 `engine: playwright`，再运行，日志显示 `PlaywrightEngine`。
3. 结果对比：两次运行结果应完全一致，证明引擎无关性。

```bash
# 直接用 CLI 指定引擎，不必改配置文件
python main.py -e playwright
python main.py -e selenium
```

```
┌─ 控制台（示意）────────────────────────────────────────┐
│ [EasyWeb] Engine: SeleniumEngine     ← 红框:默认      │
│ # 改为 playwright 后                                │
│ [EasyWeb] Engine: PlaywrightEngine   ← 红框:切换后    │
└──────────────────────────────────────────────────────┘
```

> ⚠️ 注意：
> - Playwright 需额外执行 `playwright install` 安装浏览器驱动。
> - Selenium 用项目内置 `pkg/chrome-win64` 和 `pkg/chromedriver-win64`，开箱即用。
> - 切换引擎后先跑少量用例验证环境。

### 2.5 功能五：Allure 报告

**生成**：测试跑完自动在 `allure-report/` 生成 HTML。

**查看**：

```bash
# 方式1：双击打开
allure-report\index.html

# 方式2：命令行打开
pkg\allurec\bin\allure open allure-report
```

**报告核心模块**

| 模块 | 说明 |
|------|------|
| Behaviors | 按 Epic/Feature/Story 分类的用例树 |
| Suites | 按测试文件/类分组的用例列表 |
| Categories | 缺陷分类、优先级统计 |
| Graphs | 通过率、耗时趋势、重试统计 |
| Timeline | 用例执行时间轴 |
| Test Case | 单用例详情：步骤、日志、截图、附件 |

> 💡 失败用例自动附加浏览器截图和详细日志，点 Attachments 即可查看。

```
┌─ Allure 报告（示意）──────────────────────────────────┐
│ Overview | Behaviors | Suites | Graphs | Timeline      │
│ 通过率 100%  用例数 12  失败 0   ← 红框:看这行        │
│ Test Cases → TC001 → Attachments(截图/日志)            │
└──────────────────────────────────────────────────────┘
```

---

## 三、实战示例

用一个完整用例串起各功能：**用 Excel 维护一条搜索用例 → Selenium 跑通 → 切 Playwright 复跑 → 看 Allure 报告**。

### 3.1 项目背景

验证内置测试网站首页搜索功能。日常维护用 Excel，CI 集成用 JSON；并验证双引擎结果一致。

### 3.2 完整操作流程

**第 1 步：在 Excel 写用例**（首行表头，第二行数据）

| id | name | type | url | selector | value | expected_type | expected_value | priority | description |
|----|------|------|-----|----------|-------|---------------|----------------|----------|-------------|
| TC001 | 搜索Selenium | search | ${base_url}/ | #search-input | selenium | title | 搜索 | P0 | 验证首页搜索 |

**第 2 步：Selenium 引擎运行**

```bash
python main.py -t search
```

控制台看到 `Engine: SeleniumEngine` 且 `TC001 PASSED`。

**第 3 步：切 Playwright 复跑**

改 `config/settings.yaml` 为 `engine: playwright`（或 `python main.py -t search -e playwright`），再跑一次，结果应一致。

**第 4 步：看报告**

```bash
pkg\allurec\bin\allure open allure-report
```

### 3.3 最终结果

```
┌─ 运行结果（示意）──────────────────────────────────────┐
│ Selenium:  TC001 PASSED                                 │
│ Playwright: TC001 PASSED   ← 红框:双引擎结果一致        │
│ Allure: 通过率 100%  失败 0                             │
└──────────────────────────────────────────────────────┘
```

---

## 四、踩坑记录

### 坑 1：`python main.py` 报 Python 版本过低

**现象**：启动即报错退出。
**解决**：框架要求 Python 3.11+，用 `python --version` 确认，升级到 3.11 以上。

### 坑 2：访问 http://localhost:5000 打不开

**现象**：用例跑起来但连不上网站。
**排查**：是否用了 `--no-website` 又没手动起网站；`config/settings.yaml` 里 `website_port` 与访问端口是否都是 5000；`auto_start_website` 拼写是否为布尔值 `true`。

### 坑 3：Playwright 运行报找不到浏览器

**现象**：切到 playwright 后报错。
**解决**：执行 `playwright install` 安装浏览器驱动；Selenium 则无需（用内置 chrome）。

### 坑 4：XPath 用例没生效 / 仍按 css 解析

**现象**：写了 `//input[@id='x']` 却被当 css。
**原因**：没显式加 `"by": "xpath"`。
**解决**：xpath / link_text / partial_link_text / tag_name 都必须写 `by` 字段，只有 css（含 `#id`、`.class`、`[name=]`）可省略。

### 坑 5：`${base_url}` 没被替换

**现象**：用例 url 原样带着 `${base_url}`。
**解决**：确认 `config/settings.yaml` 里 `base_url` 已配置且与端口一致；字段名拼写正确。

### 坑 6：Excel 多 Sheet 没合并 / 读数异常

**现象**：第二个 Sheet 的用例没跑。
**解决**：框架自动合并多 Sheet，检查表头是否与标准字段完全一致（首行必须是标准字段名），无多余空格。

### 坑 7：动态元素定位不稳定

**现象**：时而找到时而找不到。
**解决**：优先 css 组合选择器（如 `div.form > input[type='text']`）；动态 ID 用 xpath 的 `contains()` / `starts-with()`；框架已内置 `wait_for_element` 显式等待，避免 `time.sleep` 硬编码。

### 坑 8：报告打开是空白页

**现象**：直接双击 `index.html` 空白。
**解决**：Allure 报告需通过 `allure open` 或本地服务打开，双击 file:// 会因资源限制空白。用 `pkg\allurec\bin\allure open allure-report`。

---

## 五、总结

### 优点

- 数据驱动：新增用例只加一行 Excel/JSON，不用改 Python 代码
- 双引擎：Selenium / Playwright 配置切换，代码数据零改动
- 内置测试网站 + 浏览器/驱动，开箱即用（Git LFS 已带）
- 完整日志（控制台+文件）+ 失败自动截图 + Allure 专业报告
- 标准字段规范跨项目通用，业务与代码解耦

### 缺点

- 团队自研，依赖原作者维护与培训（作者：孙文龙）
- 定位能力封装在标准字段内，超复杂场景灵活度不如直接写代码
- 仓库为大文件（浏览器/驱动），clone 依赖 Git LFS
- 文档标注「内部项目，禁止私自传播」，需注意合规

### 适用场景

- Web 功能自动化回归（数据驱动，测试人员主导维护）
- 需要 Selenium/Playwright 双引擎对比验证的团队
- CI 流水线集成（JSON 数据 + `--no-report` 提速 + 命令过滤）
- 不适合：纯前端无标准字段结构的系统、需要高度自定义断言逻辑的场景

---

### 速查表

| 功能 | 写法 |
|------|------|
| 获取项目 | `git clone https://gitcode.com/gcw_OIVuYjdN/sun-EasyWeb.git` |
| 装依赖 | `pip install -r requirements.txt` |
| 一键运行 | 双击 `run_tests.bat` 或 `python main.py` |
| 按类型跑 | `python main.py -t login` |
| 切引擎 | `config/settings.yaml` 改 `engine: playwright` 或 `-e playwright` |
| 指定数据 | `python main.py -d data/test_data.json` |
| 注入 Cookie | `python main.py -C "token=abc123"` |
| 看报告 | `pkg\allurec\bin\allure open allure-report` |
| 必填字段 | `id` `name` `type` `url` `expected_type` `expected_value` |
| 路由依据 | `type`（search/login/nav/locator）|
| 断言依据 | `expected_type`（title/text/url/value/click）|
| xpath 必写 | `"by": "xpath"` + `selector` 用 `//` 表达式 |
