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