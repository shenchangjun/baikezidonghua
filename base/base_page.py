from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)  # 显式等待10秒

    # 核心：封装多种元素定位方式（满足至少3种定位要求）
    def find_element(self, locator_type, locator_value):
        """
        支持的定位方式：id、xpath、css_selector、name、class_name
        """
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

    # 封装通用点击操作（常规点击）
    def click_element(self, locator_type, locator_value):
        element = self.find_element(locator_type, locator_value)
        element.click()

    # 封装 JS 点击（绕过遮挡/非可见区域导致的 click intercepted）
    def click_element_by_js(self, locator_type, locator_value):
        element = self.find_element(locator_type, locator_value)
        self.driver.execute_script("arguments[0].click();", element)

    # 封装通用输入操作
    def input_text(self, locator_type, locator_value, text):
        element = self.find_element(locator_type, locator_value)
        element.clear()
        element.send_keys(text)

    # 封装获取元素文本操作
    def get_element_text(self, locator_type, locator_value):
        element = self.find_element(locator_type, locator_value)
        return element.text

    # 封装统计匹配元素数量（用于验证列表/区块是否渲染）
    def count_elements(self, locator_type, locator_value):
        if locator_type == "css_selector":
            by = "css selector"
        elif locator_type == "class_name":
            by = "class name"
        else:
            by = locator_type
        return len(self.driver.find_elements(by, locator_value))

    # 封装切换窗口操作
    def switch_to_new_window(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])

    # 封装页面滚动操作
    def scroll_to_element(self, locator_type, locator_value):
        element = self.find_element(locator_type, locator_value)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)