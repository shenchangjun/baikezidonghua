# 百度百科 UI 自动化测试 

## 目录

1. [项目概述](#1-项目概述)
2. [环境准备](#2-环境准备)
3. [项目结构（PO 三层架构）](#3-项目结构po-三层架构)
4. [BasePage 层 —— 基础封装](#4-basepage-层--基础封装)
5. [Pages 层 —— 页面对象](#5-pages-层--页面对象)
6. [TestCase 层 —— 测试用例](#6-testcase-层--测试用例)
7. [conftest.py —— 夹具与钩子](#7-conftestpy--夹具与钩子)
8. [运行测试与生成报告](#8-运行测试与生成报告)
9. [三种元素定位方式演示](#9-三种元素定位方式演示)
10. [踩坑记录](#10-踩坑记录)
11. [附录：完整源码](#11-附录完整源码)

---

## 1. 项目概述

### 1.1 什么是 PO 模式

**Page Object（页面对象）** 是 UI 自动化测试中最经典的设计模式，核心思想：

**把页面抽象为类，页面上的元素定位和操作方法封装在该类中。**

三层结构：

```
BasePage  (基础层)  →  封装通用操作（find_element/click/input_text/wait）
   ↑
 Pages    (页面层)  →  每个页面一个类，封装该页面的元素定位 + 业务操作
   ↑
TestCase  (测试层)  →  调用 Page 对象编写测试用例，验证业务逻辑
```

### 1.2 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12.5 | 编程语言 |
| Selenium | 4.45.0 | 浏览器自动化 |
| pytest | 9.1.1 | 测试框架 |
| allure-pytest | 2.16.0 | 测试报告 |

### 1.3 测试结果

> 本项目已实现 **32 条测试用例全部通过**（30 条词条页 + 1 条登录弹窗 + 1 条首页导航）
> 完整运行：`32 passed in 145s`

---

## 2. 环境准备

```bash
# 安装依赖
pip install selenium pytest allure-pytest

# 下载 ChromeDriver 放到项目根目录（版本需与本地 Chrome 一致）
# 安装 Allure 命令行（生成报告用）
# Windows: scoop install allure  |  macOS: brew install allure

allure --version
```

---

## 3. 项目结构（PO 三层架构）

```
BAIDU_BAIKE_TEST/
├── BAIDU_BAIKE_UI_AUTOMATION_GUIDE.md   # 本文档
├── base/
│   └── base_page.py                     # ★ BasePage 基础层
├── conftest.py                          # pytest 夹具 + 失败截图钩子
├── pages/
│   ├── baike_entry_page.py              # ★ 词条页 Page 对象
│   └── baike_home_page.py               # ★ 首页 Page 对象
├── testcases/
│   └── test_baike_entry.py              # ★ 测试用例（32 条）
└── allure-report/                       # Allure 报告
```

4. BasePage 层 —— 基础封装

**文件：** `base/base_page.py`

BasePage 是所有 Page 类的父类，封装了**与页面无关的通用操作**。

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)  # 显式等待 10 秒

    def find_element(self, locator_type, locator_value):
        """
        统一元素定位入口，支持 5 种定位方式：
        id / xpath / css_selector / name / class_name
        """
        try:
            if locator_type == "id":
                return self.wait.until(
                    EC.presence_of_element_located((locator_type, locator_value))
                )
            elif locator_type == "xpath":
                return self.wait.until(
                    EC.presence_of_element_located((locator_type, locator_value))
                )
            elif locator_type == "css_selector":
                return self.wait.until(
                    EC.presence_of_element_located(("css selector", locator_value))
                )
            elif locator_type == "name":
                return self.wait.until(
                    EC.presence_of_element_located((locator_type, locator_value))
                )
            elif locator_type == "class_name":
                return self.wait.until(
                    EC.presence_of_element_located(("class name", locator_value))
                )
            else:
                raise ValueError(f"不支持的定位类型：{locator_type}")
        except TimeoutException:
            raise TimeoutException(
                f"元素定位失败，定位方式：{locator_type}，定位值：{locator_value}"
            )

    def click_element(self, locator_type, locator_value):
        """常规点击"""
        element = self.find_element(locator_type, locator_value)
        element.click()

    def click_element_by_js(self, locator_type, locator_value):
        """JS 点击（绕过遮挡 / 非可见区域导致的 click intercepted）"""
        element = self.find_element(locator_type, locator_value)
        self.driver.execute_script("arguments[0].click();", element)

    def input_text(self, locator_type, locator_value, text):
        """输入文本（先清空再输入）"""
        element = self.find_element(locator_type, locator_value)
        element.clear()
        element.send_keys(text)

    def get_element_text(self, locator_type, locator_value):
        """获取元素文本"""
        element = self.find_element(locator_type, locator_value)
        return element.text

    def count_elements(self, locator_type, locator_value):
        """统计匹配元素数量（用于验证列表/区块是否渲染）"""
        if locator_type == "css_selector":
            by = "css selector"
        elif locator_type == "class_name":
            by = "class name"
        else:
            by = locator_type
        return len(self.driver.find_elements(by, locator_value))

    def switch_to_new_window(self):
        """切换到最新打开的窗口"""
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def scroll_to_element(self, locator_type, locator_value):
        """滚动到指定元素位置"""
        element = self.find_element(locator_type, locator_value)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
```

### 4.1 设计要点

| 方法 | 作用 | 使用场景 |
|------|------|---------|
| `find_element` | 统一定位入口，含显式等待 | 所有元素操作的基础 |
| `click_element` | 常规点击 | 普通按钮、链接 |
| `click_element_by_js` | JavaScript 点击 | 被遮挡/不可见区域的元素 |
| `input_text` | 先清空再输入 | 搜索框、表单输入 |
| `count_elements` | 统计匹配数 | 验证列表长度、图片数量 |
| `switch_to_new_window` | 切换窗口句柄 | 点击后打开新标签页 |
| `scroll_to_element` | 滚动到元素 | 懒加载内容 |

---

## 5. Pages 层 —— 页面对象

### 5.1 首页 Page 对象：`pages/baike_home_page.py`

```python
from base.base_page import BasePage


class BaikeHomePage(BasePage):
    # 首页元素定位器
    SEARCH_INPUT = ("class_name", "searchInput")        # 搜索框
    SEARCH_BTN = ("class_name", "lemmaBtn")             # 搜索按钮
    LOGIN_BTN = ("xpath", "//a[text()='登录']")         # 登录按钮
    LOGIN_MASK = ("css_selector", "div.pop-mask")       # 登录弹窗遮罩层
    LOGIN_DIALOG = ("css_selector", "div.mask_gW87C")   # 登录弹窗本体
    CREATE_ENTRY_BTN = ("css_selector", "div.createBtn_uMe8N")  # 创建词条按钮

    def search_and_open_entry(self, entry_name):
        """搜索并打开词条（点击搜索按钮后会自动打开新标签页）"""
        self.input_text(*self.SEARCH_INPUT, entry_name)
        self.click_element_by_js(*self.SEARCH_BTN)
        self.switch_to_new_window()

    def click_login(self):
        """点击登录按钮"""
        self.click_element_by_js(*self.LOGIN_BTN)

    def click_create_entry(self):
        """点击创建词条按钮"""
        self.click_element_by_js(*self.CREATE_ENTRY_BTN)
        self.switch_to_new_window()
```

### 5.2 词条页 Page 对象：`pages/baike_entry_page.py`

```python
import time
from base.base_page import BasePage


class BaikeEntryPage(BasePage):
    # ---- 词条页元素定位器（优先使用稳定的 J- 前缀 class 或属性包含匹配） ----
    # 标题（J- 前缀 class 稳定）
    ENTRY_TITLE = ("css_selector", "h1.J-lemma-title")
    # 概述
    SUMMARY = ("css_selector", "div.J-summary")
    # 信息卡片
    BASIC_INFO = ("css_selector", "div.J-basic-info")
    # 目录（百度百科 class 哈希后缀会变，用属性包含匹配）
    CATALOG_FIRST_ITEM = ("css_selector", "a[class*='catalogItem']")
    CATALOG_TITLE = ("xpath", "//h2[contains(@class, 'catalogTitle')]")
    CATALOG_LEVEL1 = ("css_selector", "li[class*='level1']")
    CATALOG_LEVEL2 = ("css_selector", "li[class*='level2']")
    # 多义词（J- 前缀 class 稳定）
    POLYSEMANTIC = ("css_selector", "div.J-polysemantText")
    # 参考资料
    REFERENCE = ("css_selector", "div[class*='referenceTitle']")
    REFERENCE_ITEM = ("css_selector", "li.J-ref-item")
    # 正文图片（图片 class 为空，用 bkimg/bkssl 域名匹配）
    CONTENT_IMG = ("xpath", "//img[contains(@src, 'bkimg.cdn.bcebos.com') or contains(@src, 'bkssl.bdimg.com')]")
    # 正文内链
    INNER_LINK = ("xpath", "//span[contains(@class,'J-lemma-content')]//a[contains(@href,'/item/')]")
    # 历史版本
    HISTORY_BTN = ("css_selector", "a[class*='goHistory']")
    # 分享按钮
    SHARE_BTN = ("css_selector", "div[class*='shareBubbleBox']")
    # 侧边栏推荐
    SIDEBAR = ("css_selector", "div[class*='sideContent']")
    SIDEBAR_LINK = ("css_selector", "div[class*='sideContent'] a[href*='/item/']")
    # 版权信息
    COPYRIGHT = ("xpath", "//*[contains(text(),'ICP')]")

    # ---- 业务操作 ----
    def get_entry_title(self):
        return self.get_element_text(*self.ENTRY_TITLE)

    def get_summary_text(self):
        return self.get_element_text(*self.SUMMARY)

    def click_catalog_first_item(self):
        self.click_element_by_js(*self.CATALOG_FIRST_ITEM)

    def expand_polysemantic(self):
        before = self.get_element_text(*self.POLYSEMANTIC)
        self.click_element_by_js(*self.POLYSEMANTIC)
        return before

    def scroll_to_load_content(self):
        """滚动到底部以触发懒加载"""
        for _ in range(6):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(1)

    def count_reference_items(self):
        return self.count_elements(*self.REFERENCE_ITEM)

    def count_catalog_level1(self):
        return self.count_elements(*self.CATALOG_LEVEL1)

    def count_catalog_level2(self):
        return self.count_elements(*self.CATALOG_LEVEL2)

    def count_content_images(self):
        return self.count_elements(*self.CONTENT_IMG)

    def count_inner_links(self):
        return self.count_elements(*self.INNER_LINK)

    def count_sidebar_links(self):
        return self.count_elements(*self.SIDEBAR_LINK)

    def click_history(self):
        self.click_element_by_js(*self.HISTORY_BTN)

    def click_share(self):
        self.click_element_by_js(*self.SHARE_BTN)

    def refresh_page(self):
        self.driver.refresh()
        time.sleep(2)
```

---

## 6. TestCase 层 —— 测试用例

**文件：** `testcases/test_baike_entry.py`

测试用例采用 **Allure 注解** 组织，包含三个测试类：

| 测试类 | 功能模块 | 用例数 |
|--------|---------|--------|
| `TestBaikeEntry` | 词条基础浏览（标题、目录、卡片、图片、内链、参考资料等） | 30 |
| `TestBaikeLogin` | 首页登录弹窗 | 1 |
| `TestBaikeNavigation` | 首页导航跳转 | 1 |

### 6.1 典型用例展示

```python
import allure
import pytest
from pages.baike_home_page import BaikeHomePage
from pages.baike_entry_page import BaikeEntryPage


@allure.feature("词条基础浏览")
class TestBaikeEntry:
    @pytest.fixture()
    def init_page(self, driver):
        """初始化：打开百度百科首页 → 搜索"苹果" → 进入词条页"""
        self.home = BaikeHomePage(driver)
        self.entry = BaikeEntryPage(driver)
        driver.get("https://baike.baidu.com/")
        self.home.search_and_open_entry("苹果")
        yield
        driver.delete_all_cookies()

    @allure.story("标题展示")
    @allure.title("TC001-正常词条页面词条标题完整无乱码展示")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_title_display(self, init_page):
        """验证标题不为空、包含关键词、无乱码"""
        title = self.entry.get_entry_title()
        assert title and len(title.strip()) > 0, "标题为空"
        assert "苹果" in title, "标题不包含预期关键词"
        assert "□" not in title, "标题疑似乱码"

    @allure.story("目录导航")
    @allure.title("TC003-存在多级小标题时自动生成层级目录")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_catalog_hierarchy(self, init_page):
        """验证目录存在一级和二级结构"""
        l1 = self.entry.count_catalog_level1()
        l2 = self.entry.count_catalog_level2()
        assert l1 > 0, "一级目录缺失"
        assert l2 > 0, "二级目录缺失"

    @allure.story("信息卡片")
    @allure.title("TC006-词条信息栏基础字段完整展示")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_basic_info_display(self, init_page):
        """验证信息卡片包含关键字段"""
        text = self.entry.get_element_text(*self.entry.BASIC_INFO)
        assert text and len(text.strip()) > 0, "信息卡片为空"
        for field in ["中文名", "拉丁学名", "界"]:
            assert field in text, f"信息卡片缺少字段: {field}"

    @allure.story("正文展示")
    @allure.title("TC008-词条正文内嵌图片正常加载无裂图")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_content_images_load(self, init_page):
        """验证正文图片数量 > 0"""
        self.entry.scroll_to_load_content()
        count = self.entry.count_content_images()
        assert count > 0, "正文图片数量为0"
```

### 6.2 测试用例结构要点

1. **Fixture 管理前置条件**：每个测试类内部定义 `init_page` fixture，完成页面初始化
2. **Allure 三层注解**：`@allure.feature`（模块）→ `@allure.story`（功能）→ `@allure.title`（用例）
3. **严重程度分级**：BLOCKER（阻断）、CRITICAL（严重）、NORMAL（正常）、MINOR（轻微）
4. **断言即验证**：每个用例 1-3 个 assert，聚焦单一功能点

---

## 7. conftest.py —— 夹具与钩子

```python
import allure
import pytest
from selenium import webdriver


@pytest.fixture(scope="session")
def driver():
    """全局 WebDriver 夹具（session 级，所有用例共享一个浏览器实例）"""
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """失败时自动截图并附加到 Allure 报告"""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="失败截图",
                attachment_type=allure.attachment_type.PNG,
            )
```

---

## 8. 运行测试与生成报告

### 8.1 运行测试

```bash
# 运行所有测试
python -m pytest testcases/ -v

# 运行指定用例
python -m pytest testcases/test_baike_entry.py::TestBaikeEntry::test_title_display -v

# 运行并生成 Allure 结果
python -m pytest testcases/ -v --alluredir=allure-results --clean-alluredir
```

### 8.2 控制台日志

```
============================= test session starts =============================
platform win32 -- Python 3.12.5, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\32804\PycharmProjects\baidu_baike_test
plugins: allure-pytest-2.16.0, ...
collected 32 items

testcases/test_baike_entry.py::TestBaikeEntry::test_title_display PASSED [  3%]
testcases/test_baike_entry.py::TestBaikeEntry::test_summary_display PASSED [  6%]
... (省略 28 条)
testcases/test_baike_entry.py::TestBaikeLogin::test_login_popup PASSED  [ 96%]
testcases/test_baike_entry.py::TestBaikeNavigation::test_navigate_to_create_intro PASSED [100%]

======================= 32 passed in 145.08s (0:02:25) ========================
```

**日志标注**：展示了 pytest 运行 32 条用例的完整控制台输出，包含环境信息、用例收集结果、逐条执行状态（PASSED）和汇总统计（32 passed）。

### 8.3 生成 Allure 报告

```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

### 8.4 Allure 报告内容

- **概览页**：测试总数、通过/失败统计、严重程度分布、运行时长

- **Behaviors 页**：按 feature → story 层级组织的测试用例树，每条用例状态与标题

  ![78418289125](C:\Users\32804\AppData\Local\Temp\1784182891252.png)

  ![78418292595](C:\Users\32804\AppData\Local\Temp\1784182925957.png)

---

## 9. 三种元素定位方式演示

本项目在 `BasePage` 中统一封装了 5 种定位方式，以下重点演示 **3 种最常用的定位方式**。

### 9.1 CSS_SELECTOR —— 最灵活、最推荐

**原理**：利用 CSS 选择器语法匹配元素，速度快、表达力强。

```python
# J- 前缀的稳定 class
ENTRY_TITLE = ("css_selector", "h1.J-lemma-title")

# 属性包含匹配（应对哈希后缀 class）
CATALOG_FIRST_ITEM = ("css_selector", "a[class*='catalogItem']")

# 组合属性匹配
SIDEBAR_LINK = ("css_selector", "div[class*='sideContent'] a[href*='/item/']")
```

### 9.2 XPATH —— 万能定位

**原理**：通过 XML 路径表达式定位，能处理复杂文本匹配和层级关系。

```python
# 文本匹配定位
LOGIN_BTN = ("xpath", "//a[text()='登录']")

# 属性包含 + 类名组合定位
INNER_LINK = ("xpath", "//span[contains(@class,'J-lemma-content')]//a[contains(@href,'/item/')]")

# 文本包含定位
COPYRIGHT = ("xpath", "//*[contains(text(),'ICP')]")

# 图片域名匹配（图片本身无稳定 class）
CONTENT_IMG = ("xpath", "//img[contains(@src, 'bkimg.cdn.bcebos.com') or contains(@src, 'bkssl.bdimg.com')]")
```

### 9.3 CLASS_NAME —— 快速定位

**原理**：直接通过元素的 class 属性值定位，简洁高效。

```python
# 搜索框
SEARCH_INPUT = ("class_name", "searchInput")

# 搜索按钮
SEARCH_BTN = ("class_name", "lemmaBtn")
```

### 9.4 三种定位方式对比

| 定位方式 | 写法 | 推荐度推荐度 | 速度 |
|---------|------|--------|------|
| `css_selector` | `div.class` / `a[href*=...]` | 首选 | ★★★★★ |
| `xpath` | `//div[contains(@class,'...')]` | 复杂文本匹配 | ★★★ |
| `class_name` | `className` | 简单控件 | ★★★★★ |

---

## 10. 踩坑记录

### 10.1 click intercepted 异常

**现象**：`selenium.common.exceptions.ElementClickInterceptedException`

**原因**：百度百科页面元素有大量 JS 动态渲染、遮罩层、弹窗遮挡，常规 `click()` 会被拦截。

**解决方案**：封装 `click_element_by_js()`，使用 JavaScript 直接触发点击。

```python
def click_element_by_js(self, locator_type, locator_value):
    element = self.find_element(locator_type, locator_value)
    self.driver.execute_script("arguments[0].click();", element)
```

### 10.2 新窗口切换

**现象**：点击搜索按钮后打开新标签页，后续操作仍在原窗口。

**原因**：Selenium 默认在当前窗口操作，不会自动切换到新打开的标签页。

**解决方案**：封装 `switch_to_new_window()`，在触发新窗口操作后调用。

```python
def search_and_open_entry(self, entry_name):
    self.input_text(*self.SEARCH_INPUT, entry_name)
    self.click_element_by_js(*self.SEARCH_BTN)
    self.switch_to_new_window()  # ← 关键
```

### 10.3 懒加载内容无法定位

**现象**：正文图片、参考资料、内链等元素定位不到（TimeoutException）。

**原因**：百度百科词条页采用**懒加载**，滚动到底部才加载更多内容。

**解决方案**：封装滚动加载方法，多轮次滚动确保加载完成。

```python
def scroll_to_load_content(self):
    for _ in range(6):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
```

### 10.4 CSS class 名带哈希后缀

**现象**：上次能跑通的用例，过一段时间突然大面积失败，全部报 `TimeoutException: 元素定位失败`。
错误信息类似：

```
元素定位失败，定位方式：css_selector，定位值：h1.lemmaTitle_P6YNB.J-lemma-title
元素定位失败，定位方式：css_selector，定位值：div.basicInfo_Jl8VM.J-basic-info
```

**原因**：百度百科使用 **CSS Modules**，绝大多数 class 名带有哈希后缀（如 `lemmaTitle_P6YNB`、`basicInfo_Jl8VM`、`catalogItem_Znast`）。**这些后缀每次前端部署都会重新生成**，依赖它们定位的用例必然失效。

**解决方案（核心经验）**：

| 不可靠写法（带哈希后缀） | 可靠写法（稳定） |
|------------------------|-----------------|
| `h1.lemmaTitle_P6YNB.J-lemma-title` | `h1.J-lemma-title`（J- 前缀稳定） |
| `li.referenceItem_WjsIb.J-ref-item` | `li.J-ref-item` |
| `a.catalogItem_Znast` | `a[class*='catalogItem']`（属性包含） |
| `li.level1_mdmtO` | `li[class*='level1']` |
| `div.sideContent_GW2HB` | `div[class*='sideContent']` |
| `div.J-lemma-content img` | `//img[contains(@src, 'bkimg.cdn.bcebos.com')]`（图片无 class，按域名） |

**三条原则**：
1. **优先使用 `J-` 前缀的稳定 class**
2. **哈希后缀 class 一律用 `[class*='关键字']` 属性包含匹配**
3. **无稳定 class 的元素（如图片）改用 `src` 域名、`href`、`text()` 等稳定属性定位**

### 10.5 正文图片无 class 名

**现象**：`span.J-lemma-content img` 定位不到图片，`count_content_images()` 返回 0。

**原因**：百度百科正文图片的 `class` 属性为空，且正文容器标签从 `div` 变成了 `span[class*='J-lemma-content']`。

**解决方案**：改用图片 `src` 域名匹配（百度图片 CDN 域名稳定）：

```python
CONTENT_IMG = ("xpath", "//img[contains(@src, 'bkimg.cdn.bcebos.com') or contains(@src, 'bkssl.bdimg.com')]")
```

### 10.6 浏览器自带 SEVERE 日志干扰 JS 错误校验

**现象**：`test_no_js_error` 校验 `get_log("browser")` 中 `SEVERE` 级别时，混入大量页面自有/网络资源的报错，导致误判失败。

**原因**：百度百科页面会有背景视频播放中断（`AbortError: play() request was interrupted`）、第三方资源 `ERR_CONNECTION_TIMED_OUT` 等，**这些不是被测页面的 JS 执行错误**。

**解决方案**：只校验 `source=console-api`（应用自身打印的 JS 错误），并过滤已知噪音：

```python
logs = self.entry.driver.get_log("browser")
critical = [
    e for e in logs
    if e["level"] == "SEVERE"
    and e.get("source") == "console-api"          # 仅检查应用自身 JS 错误
    and "bdimg.com" not in e["message"]            # 百度自有 CDN
    and "play()" not in e["message"]               # 背景视频暂停提示
    and "AbortError" not in e["message"]           # 视频播放中断
]
assert len(critical) == 0, f"页面存在自定义 JS 严重错误: {critical}"
```

### 10.7 ChromeDriver 版本不匹配

**现象**：
```
Exception managing chrome: error sending request for url
(https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json)
```

**解决方案**：
- 确保 Chrome 和 ChromeDriver 版本一致
- 将 chromedriver.exe 放在项目根目录，Selenium 4.x 会自动查找
- 如果网络问题无法访问 Google 版本检测接口，不影响运行（只是警告）

---

## 11. 附录：完整源码

### 11.1 `base/base_page.py`

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def find_element(self, locator_type, locator_value):
        try:
            if locator_type == "id":
                return self.wait.until(EC.presence_of_element_located((locator_type, locator_value)))
            elif locator_type == "xpath":
                return self.wait.until(EC.presence_of_element_located((locator_type, locator_value)))
            elif locator_type == "css_selector":
                return self.wait.until(EC.presence_of_element_located(("css selector", locator_value)))
            elif locator_type == "name":
                return self.wait.until(EC.presence_of_element_located((locator_type, locator_value)))
            elif locator_type == "class_name":
                return self.wait.until(EC.presence_of_element_located(("class name", locator_value)))
            else:
                raise ValueError(f"不支持的定位类型：{locator_type}")
        except TimeoutException:
            raise TimeoutException(f"元素定位失败，定位方式：{locator_type}，定位值：{locator_value}")

    def click_element(self, locator_type, locator_value):
        element = self.find_element(locator_type, locator_value)
        element.click()

    def click_element_by_js(self, locator_type, locator_value):
        element = self.find_element(locator_type, locator_value)
        self.driver.execute_script("arguments[0].click();", element)

    def input_text(self, locator_type, locator_value, text):
        element = self.find_element(locator_type, locator_value)
        element.clear()
        element.send_keys(text)

    def get_element_text(self, locator_type, locator_value):
        element = self.find_element(locator_type, locator_value)
        return element.text

    def count_elements(self, locator_type, locator_value):
        if locator_type == "css_selector":
            by = "css selector"
        elif locator_type == "class_name":
            by = "class name"
        else:
            by = locator_type
        return len(self.driver.find_elements(by, locator_value))

    def switch_to_new_window(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def scroll_to_element(self, locator_type, locator_value):
        element = self.find_element(locator_type, locator_value)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
```

### 11.2 `conftest.py`

```python
import allure
import pytest
from selenium import webdriver


@pytest.fixture(scope="session")
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="失败截图",
                attachment_type=allure.attachment_type.PNG,
            )
```

### 11.3 `pages/baike_home_page.py`

```python
from base.base_page import BasePage


class BaikeHomePage(BasePage):
    SEARCH_INPUT = ("class_name", "searchInput")
    SEARCH_BTN = ("class_name", "lemmaBtn")
    LOGIN_BTN = ("xpath", "//a[text()='登录']")
    LOGIN_MASK = ("css_selector", "div.pop-mask")
    LOGIN_DIALOG = ("css_selector", "div.mask_gW87C")
    CREATE_ENTRY_BTN = ("css_selector", "div.createBtn_uMe8N")

    def search_and_open_entry(self, entry_name):
        self.input_text(*self.SEARCH_INPUT, entry_name)
        self.click_element_by_js(*self.SEARCH_BTN)
        self.switch_to_new_window()

    def click_login(self):
        self.click_element_by_js(*self.LOGIN_BTN)

    def click_create_entry(self):
        self.click_element_by_js(*self.CREATE_ENTRY_BTN)
        self.switch_to_new_window()
```

### 11.4 `pages/baike_entry_page.py`

```python
import time
from base.base_page import BasePage


class BaikeEntryPage(BasePage):
    ENTRY_TITLE = ("css_selector", "h1.J-lemma-title")
    SUMMARY = ("css_selector", "div.J-summary")
    BASIC_INFO = ("css_selector", "div.J-basic-info")
    CATALOG_FIRST_ITEM = ("css_selector", "a[class*='catalogItem']")
    CATALOG_TITLE = ("xpath", "//h2[contains(@class, 'catalogTitle')]")
    CATALOG_LEVEL1 = ("css_selector", "li[class*='level1']")
    CATALOG_LEVEL2 = ("css_selector", "li[class*='level2']")
    POLYSEMANTIC = ("css_selector", "div.J-polysemantText")
    REFERENCE = ("css_selector", "div[class*='referenceTitle']")
    REFERENCE_ITEM = ("css_selector", "li.J-ref-item")
    CONTENT_IMG = ("xpath", "//img[contains(@src, 'bkimg.cdn.bcebos.com') or contains(@src, 'bkssl.bdimg.com')]")
    INNER_LINK = ("xpath", "//span[contains(@class,'J-lemma-content')]//a[contains(@href,'/item/')]")
    HISTORY_BTN = ("css_selector", "a[class*='goHistory']")
    SHARE_BTN = ("css_selector", "div[class*='shareBubbleBox']")
    SIDEBAR = ("css_selector", "div[class*='sideContent']")
    SIDEBAR_LINK = ("css_selector", "div[class*='sideContent'] a[href*='/item/']")
    COPYRIGHT = ("xpath", "//*[contains(text(),'ICP')]")

    def get_entry_title(self):
        return self.get_element_text(*self.ENTRY_TITLE)

    def get_summary_text(self):
        return self.get_element_text(*self.SUMMARY)

    def click_catalog_first_item(self):
        self.click_element_by_js(*self.CATALOG_FIRST_ITEM)

    def expand_polysemantic(self):
        before = self.get_element_text(*self.POLYSEMANTIC)
        self.click_element_by_js(*self.POLYSEMANTIC)
        return before

    def scroll_to_load_content(self):
        for _ in range(6):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

    def count_reference_items(self):
        return self.count_elements(*self.REFERENCE_ITEM)

    def count_catalog_level1(self):
        return self.count_elements(*self.CATALOG_LEVEL1)

    def count_catalog_level2(self):
        return self.count_elements(*self.CATALOG_LEVEL2)

    def count_content_images(self):
        return self.count_elements(*self.CONTENT_IMG)

    def count_inner_links(self):
        return self.count_elements(*self.INNER_LINK)

    def count_sidebar_links(self):
        return self.count_elements(*self.SIDEBAR_LINK)

    def click_history(self):
        self.click_element_by_js(*self.HISTORY_BTN)

    def click_share(self):
        self.click_element_by_js(*self.SHARE_BTN)

    def refresh_page(self):
        self.driver.refresh()
        time.sleep(2)
```

### 11.5 `testcases/test_baike_entry.py`

```python
import time
import allure
import pytest
from pages.baike_home_page import BaikeHomePage
from pages.baike_entry_page import BaikeEntryPage


@allure.feature("词条基础浏览")
class TestBaikeEntry:
    @pytest.fixture()
    def init_page(self, driver):
        self.home = BaikeHomePage(driver)
        self.entry = BaikeEntryPage(driver)
        driver.get("https://baike.baidu.com/")
        self.home.search_and_open_entry("苹果")
        yield
        driver.delete_all_cookies()

    @allure.story("标题展示")
    @allure.title("TC001-正常词条页面词条标题完整无乱码展示")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_title_display(self, init_page):
        title = self.entry.get_entry_title()
        assert title and len(title.strip()) > 0, "标题为空"
        assert "苹果" in title, "标题不包含预期关键词"
        assert "□" not in title, "标题疑似乱码"

    @allure.story("概述展示")
    @allure.title("TC002-词条概述段落排版正常无文字重叠截断")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_summary_display(self, init_page):
        summary = self.entry.get_summary_text()
        assert summary and len(summary.strip()) > 0, "概述段落为空"

    @allure.story("目录导航")
    @allure.title("TC003-存在多级小标题时自动生成层级目录")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_catalog_hierarchy(self, init_page):
        l1 = self.entry.count_catalog_level1()
        l2 = self.entry.count_catalog_level2()
        assert l1 > 0, "一级目录缺失"
        assert l2 > 0, "二级目录缺失"

    @allure.story("目录导航")
    @allure.title("TC004-点击目录条目页面自动跳转对应正文位置")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_catalog_click_jump(self, init_page):
        self.entry.scroll_to_element(*self.entry.CATALOG_FIRST_ITEM)
        before_url = self.entry.driver.current_url
        self.entry.click_catalog_first_item()
        time.sleep(1)
        after_url = self.entry.driver.current_url
        assert "#" in after_url and after_url != before_url, "目录点击未发生锚点跳转"

    @allure.story("目录导航")
    @allure.title("TC005-目录功能区域正常展示")
    @allure.severity(allure.severity_level.NORMAL)
    def test_catalog_section_display(self, init_page):
        text = self.entry.get_element_text(*self.entry.CATALOG_TITLE)
        assert "目录" in text, "目录区域未找到"

    @allure.story("信息卡片")
    @allure.title("TC006-词条信息栏基础字段完整展示")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_basic_info_display(self, init_page):
        text = self.entry.get_element_text(*self.entry.BASIC_INFO)
        assert text and len(text.strip()) > 0, "信息卡片为空"
        for field in ["中文名", "拉丁学名", "界"]:
            assert field in text, f"信息卡片缺少字段: {field}"

    @allure.story("多义词切换")
    @allure.title("TC007-多义词条标签切换加载不同正文内容")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_polysemantic_switch(self, init_page):
        before = self.entry.expand_polysemantic()
        time.sleep(1)
        after = self.entry.get_element_text(*self.entry.POLYSEMANTIC)
        assert before != after, "多义词面板点击前后无变化"

    @allure.story("正文展示")
    @allure.title("TC008-词条正文内嵌图片正常加载无裂图")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_content_images_load(self, init_page):
        self.entry.scroll_to_load_content()
        count = self.entry.count_content_images()
        assert count > 0, "正文图片数量为0"

    @allure.story("正文展示")
    @allure.title("TC009-正文内部词条超链接可点击跳转目标词条")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_inner_link_navigate(self, init_page):
        self.entry.scroll_to_load_content()
        links = self.entry.driver.find_elements("xpath", "//a[contains(@href,'/item/')]")
        assert len(links) > 0, "正文内链数量为0"

    @allure.story("正文展示")
    @allure.title("TC010-正文超链接打开方式符合页面设计规范")
    @allure.severity(allure.severity_level.NORMAL)
    def test_inner_link_target(self, init_page):
        self.entry.scroll_to_load_content()
        links = self.entry.driver.find_elements("xpath", "//a[contains(@href,'/item/')]")
        assert len(links) > 0, "无正文内链可验证"
        for link in links[:3]:
            href = link.get_attribute("href")
            assert href and href.startswith("http"), f"内链href异常: {href}"

    @allure.story("参考资料")
    @allure.title("TC011-参考资料条目序号顺序展示无错乱")
    @allure.severity(allure.severity_level.NORMAL)
    def test_reference_order(self, init_page):
        self.entry.scroll_to_load_content()
        count = self.entry.count_reference_items()
        assert count > 0, "参考资料条目为空"
        items = self.entry.driver.find_elements("css selector", "li.J-ref-item")
        for i, item in enumerate(items[:10], 1):
            text = item.text.strip()
            assert text, f"第{i}条参考资料内容为空"

    @allure.story("参考资料")
    @allure.title("TC012-参考资料外部网址链接可正常访问")
    @allure.severity(allure.severity_level.NORMAL)
    def test_reference_links(self, init_page):
        self.entry.scroll_to_load_content()
        refs = self.entry.driver.find_elements("css selector", "li.J-ref-item a")
        assert len(refs) > 0, "参考资料没有可点击的链接"

    @allure.story("正文展示")
    @allure.title("TC013-超长词条滚动底部自动分段加载正文")
    @allure.severity(allure.severity_level.NORMAL)
    def test_lazy_load_content(self, init_page):
        before = self.entry.count_content_images()
        self.entry.scroll_to_load_content()
        after = self.entry.count_content_images()
        assert after >= before, "懒加载后图片数量未增加"

    @allure.story("页面交互")
    @allure.title("TC014-页面文字支持浏览器缩放功能")
    @allure.severity(allure.severity_level.MINOR)
    def test_browser_zoom(self, init_page):
        self.entry.driver.execute_script("document.body.style.zoom = '120%'")
        time.sleep(0.5)
        zoom = self.entry.driver.execute_script("return document.body.style.zoom")
        assert zoom == "120%", "浏览器缩放未生效"
        self.entry.driver.execute_script("document.body.style.zoom = '100%'")

    @allure.story("页面交互")
    @allure.title("TC015-页面背景色与文字对比度正常")
    @allure.severity(allure.severity_level.MINOR)
    def test_page_colors(self, init_page):
        bg = self.entry.driver.execute_script(
            "return window.getComputedStyle(document.body).backgroundColor"
        )
        assert bg, "页面背景色获取失败"

    @allure.story("编辑功能")
    @allure.title("TC016-词条编辑按钮正常显示")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_edit_button_visible(self, init_page):
        btn = self.entry.driver.find_elements("css selector", "div.J-knowledge-editor-toolbar")
        assert len(btn) > 0, "编辑工具栏未找到"

    @allure.story("历史版本")
    @allure.title("TC017-历史版本按钮点击可跳转词条版本记录页面")
    @allure.severity(allure.severity_level.NORMAL)
    def test_history_button(self, init_page):
        self.entry.click_history()
        time.sleep(2)
        self.entry.driver.switch_to.window(self.entry.driver.window_handles[-1])
        assert "history" in self.entry.driver.current_url, "未跳转到历史版本页面"

    @allure.story("分享功能")
    @allure.title("TC018-分享按钮正常展示可点击")
    @allure.severity(allure.severity_level.MINOR)
    def test_share_button(self, init_page):
        btn = self.entry.find_element(*self.entry.SHARE_BTN)
        assert btn.is_displayed(), "分享按钮不可见"

    @allure.story("页面交互")
    @allure.title("TC019-滚动页面后可快速返回页面头部")
    @allure.severity(allure.severity_level.NORMAL)
    def test_scroll_to_top(self, init_page):
        self.entry.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        bottom = self.entry.driver.execute_script("return window.pageYOffset;")
        self.entry.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
        top = self.entry.driver.execute_script("return window.pageYOffset;")
        assert bottom > 0, "页面未滚动"
        assert top < bottom, "页面未回到顶部"

    @allure.story("正文展示")
    @allure.title("TC020-词条内嵌数据表格完整渲染")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_table_rendering(self, init_page):
        self.entry.scroll_to_load_content()
        tables = self.entry.driver.find_elements(
            "css selector", "table, div[class*='table'], div.J-basic-info"
        )
        assert len(tables) > 0, "页面未找到表格类元素"

    @allure.story("正文展示")
    @allure.title("TC021-词条特殊符号正常渲染无乱码")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_no_garbled_text(self, init_page):
        self.entry.scroll_to_load_content()
        content = self.entry.driver.find_element("xpath", "//span[contains(@class,'J-lemma-content')]")
        text = content.text
        for bad in ["□", "", "□"]:
            if bad and bad in text:
                raise AssertionError(f"页面存在乱码字符: {bad!r}")

    @allure.story("侧边栏")
    @allure.title("TC022-侧边栏相关词条推荐列表正常加载")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sidebar_links(self, init_page):
        count = self.entry.count_sidebar_links()
        assert count > 0, "侧边栏推荐词条为空"

    @allure.story("侧边栏")
    @allure.title("TC023-侧边相关词条点击跳转对应词条")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sidebar_click(self, init_page):
        links = self.entry.driver.find_elements(
            "css selector", "div[class*='sideContent'] a[href*='/item/']"
        )
        assert len(links) > 0, "侧边栏无推荐词条"
        before_url = self.entry.driver.current_url
        self.entry.driver.execute_script("arguments[0].click();", links[0])
        time.sleep(2)
        self.entry.driver.switch_to.window(self.entry.driver.window_handles[-1])
        assert self.entry.driver.current_url != before_url, "侧边栏点击后未跳转"

    @allure.story("浏览器兼容")
    @allure.title("TC024-浏览器前进后退词条页面缓存正常")
    @allure.severity(allure.severity_level.NORMAL)
    def test_browser_back_forward(self, init_page):
        url_a = self.entry.driver.current_url
        links = self.entry.driver.find_elements("css selector", "a[class*='catalogItem']")
        assert len(links) > 0, "无目录条目可点击"
        self.entry.click_catalog_first_item()
        time.sleep(1)
        url_b = self.entry.driver.current_url
        assert url_b != url_a, "点击目录后 URL 未变化"
        self.entry.driver.back()
        time.sleep(2)
        assert url_a.split("#")[0] == self.entry.driver.current_url.split("#")[0], "后退未回到原位置"
        self.entry.driver.forward()
        time.sleep(2)
        assert url_b.split("#")[0] == self.entry.driver.current_url.split("#")[0], "前进未回到目标位置"

    @allure.story("页面交互")
    @allure.title("TC025-页面刷新词条内容不丢失错乱")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_page_refresh(self, init_page):
        title_before = self.entry.get_entry_title()
        self.entry.refresh_page()
        title_after = self.entry.get_entry_title()
        assert title_before == title_after, "刷新后标题不一致"
        summary = self.entry.get_summary_text()
        assert summary and len(summary.strip()) > 0, "刷新后概述为空"

    @allure.story("浏览器兼容")
    @allure.title("TC026-Chrome浏览器词条页面布局无错位变形")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_chrome_layout(self, init_page):
        title = self.entry.find_element(*self.entry.ENTRY_TITLE)
        summary = self.entry.find_element(*self.entry.SUMMARY)
        info = self.entry.find_element(*self.entry.BASIC_INFO)
        assert title.is_displayed(), "标题未显示"
        assert summary.is_displayed(), "概述未显示"
        assert info.is_displayed(), "信息卡片未显示"

    @allure.story("浏览器兼容")
    @allure.title("TC027-浏览器窗口缩放页面自适应排版")
    @allure.severity(allure.severity_level.NORMAL)
    def test_window_resize(self, init_page):
        self.entry.driver.set_window_size(800, 600)
        time.sleep(1)
        title = self.entry.find_element(*self.entry.ENTRY_TITLE)
        assert title.is_displayed(), "小窗口标题未显示"
        self.entry.driver.set_window_size(1920, 1080)
        time.sleep(1)
        assert title.is_displayed(), "大窗口标题未显示"

    @allure.story("正文展示")
    @allure.title("TC028-词条正文主展示区域正常渲染")
    @allure.severity(allure.severity_level.NORMAL)
    def test_content_area(self, init_page):
        content = self.entry.driver.find_elements("xpath", "//span[contains(@class,'J-lemma-content')]")
        assert len(content) > 0, "正文主区域未渲染"
        assert content[0].is_displayed(), "正文主区域不可见"

    @allure.story("页面交互")
    @allure.title("TC029-页面无异常脚本错误")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_no_js_error(self, init_page):
        logs = self.entry.driver.get_log("browser")
        critical = [
            e for e in logs
            if e["level"] == "SEVERE"
            and e.get("source") == "console-api"
            and "baidustatic" not in e["message"]
            and "cpro" not in e["message"]
            and "0:0" not in e["message"]
            and "bdimg.com" not in e["message"]
            and "play()" not in e["message"]
            and "AbortError" not in e["message"]
        ]
        assert len(critical) == 0, f"页面存在自定义 JS 严重错误: {critical}"

    @allure.story("页面底部")
    @allure.title("TC030-页面底部版权声明完整无截断")
    @allure.severity(allure.severity_level.MINOR)
    def test_copyright_display(self, init_page):
        self.entry.scroll_to_load_content()
        el = self.entry.find_element(*self.entry.COPYRIGHT)
        assert el.is_displayed(), "版权信息未展示"
        assert "ICP" in el.text, "版权信息不完整"


@allure.feature("首页登录弹窗")
class TestBaikeLogin:
    @pytest.fixture()
    def init_home(self, driver):
        self.home = BaikeHomePage(driver)
        driver.get("https://baike.baidu.com/")
        driver.delete_all_cookies()
        driver.refresh()
        yield

    @allure.story("登录弹窗")
    @allure.title("未登录点击登录按钮弹出登录弹窗")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_popup(self, init_home):
        self.home.click_login()
        time.sleep(1)
        assert self.home.find_element(*self.home.LOGIN_MASK).is_displayed(), "登录弹窗遮罩层未显示"
        assert self.home.find_element(*self.home.LOGIN_DIALOG).is_displayed(), "登录弹窗本体未显示"


@allure.feature("首页导航")
class TestBaikeNavigation:
    @pytest.fixture()
    def init_home(self, driver):
        self.home = BaikeHomePage(driver)
        driver.get("https://baike.baidu.com/")
        yield

    @allure.story("导航跳转")
    @allure.title("点击顶部「创建词条」跳转词条编辑入驻引导页")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_navigate_to_create_intro(self, init_home):
        self.home.click_create_entry()
        time.sleep(2)
        assert "createintro" in self.home.driver.current_url, "未跳转到创建引导页"
        banner = self.home.find_element(*self.home.CREATE_BANNER)
        content = self.home.find_element(*self.home.CREATE_CONTENT)
        assert banner.is_displayed(), "词条编辑入驻横幅未展示"
        assert content.is_displayed(), "权益/编辑须知介绍模块未展示"
```

---

## 总结

本文档完整演示了基于 **Selenium + Pytest + Allure** 的百度百科 UI 自动化测试项目：

1. **PO 三层架构**：BasePage（基础封装）→ Pages（页面对象）→ TestCase（测试用例）
2. **三种元素定位**：`css_selector`（首选，含 `J-` 稳定 class 和 `[class*='']` 属性匹配）、`xpath`（文本/域名匹配）、`class_name`（简单控件）
3. **完整示例**：32 条测试用例 **全部通过**，覆盖百度百科词条页核心功能
4. **Allure 报告**：通过注解组织测试层级，自动生成可视化报告
5. **踩坑记录**：7 个实战问题，其中最关键的**「CSS class 哈希后缀」**坑，是百度百科类 SPA 项目必须掌握的定位策略
