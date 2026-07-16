from base.base_page import BasePage


class BaikeHomePage(BasePage):
    # 首页元素定位器
    SEARCH_INPUT = ("class_name", "searchInput")           # 搜索框
    SEARCH_BTN = ("class_name", "lemmaBtn")                # 搜索按钮
    LOGIN_BTN = ("xpath", "//a[text()='登录']")            # 登录按钮
    LOGIN_MASK = ("css_selector", "div.pop-mask")          # 登录弹窗遮罩层
    LOGIN_DIALOG = ("css_selector", "div.mask_gW87C")      # 登录弹窗本体
    CREATE_ENTRY_BTN = ("css_selector", "div.createBtn_uMe8N")  # 创建词条按钮
    CREATE_BANNER = ("css_selector", "div.main-banner")         # 引导页横幅
    CREATE_CONTENT = ("css_selector", "div.page_content")       # 引导页内容/编辑须知

    # 首页业务操作：搜索并打开词条
    def search_and_open_entry(self, entry_name):
        self.input_text(*self.SEARCH_INPUT, entry_name)
        self.click_element_by_js(*self.SEARCH_BTN)
        self.switch_to_new_window()

    # 首页业务操作：点击登录按钮
    def click_login(self):
        self.click_element_by_js(*self.LOGIN_BTN)

    # 首页业务操作：点击创建词条按钮，跳转引导页
    def click_create_entry(self):
        self.click_element_by_js(*self.CREATE_ENTRY_BTN)
        self.switch_to_new_window()