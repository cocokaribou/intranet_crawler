from selenium import webdriver
from selenium.common.exceptions import *
from starlette.datastructures import URL
from webdriver_manager.chrome import ChromeDriverManager


class Browser:
    def __init__(self, base_domain, showScreen: bool = False):
        self.base_domain = base_domain

        options = webdriver.ChromeOptions()

        if not showScreen:
            # disable chrome options to see chrome UI
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--start-maximized")
            options.add_argument("--window-size=1200x600")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36")
            options.add_argument("--disable-gpu")
            options.add_argument("--log-level=3")  # 3 is for INFO level
            options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage
            options.add_argument("--disable-cache")

        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)

        self.driver.get(base_domain)
        self.driver.implicitly_wait(1)

    def __enter__(self):
        return self

    @property
    def current_url(self):
        return self.driver.current_url

    def implicitly_wait(self, t):
        self.driver.implicitly_wait(t)

    def find_element(self, by, value):
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            return None

    def find_multiple(self, by, value):
        try:
            return self.driver.find_elements(by, value)
        except NoSuchElementException:
            return None

    def scroll_down(self, wait=0.3):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        self.implicitly_wait(wait)

    def scroll_up(self, offset=-1, wait=2):
        if offset == -1:
            self.driver.execute_script("window.scrollTo(0, 0)")
        else:
            self.driver.execute_script("window.scrollBy(0, -%s)" % offset)
        self.implicitly_wait(wait)

    def js_click(self, elem):
        self.driver.execute_script("arguments[0].click();", elem)

    def open_new_tab(self, url):
        self.driver.execute_script("window.open('%s');" % url)
        self.driver.switch_to.window(self.driver.window_handles[1])

    def close_current_tab(self):
        self.driver.close()

        self.driver.switch_to.window(self.driver.window_handles[0])

    def execute_script(self, script: str):
        self.driver.execute_script(script)

    def switch_frame(self, frame_id: str):
        self.driver.switch_to.frame(frame_id)

    def get_cookies(self):
        return self.driver.get_cookies()

    def get_cookie(self, cookie_name: str = ""):
        if cookie_name:
            return self.driver.get_cookie(cookie_name)["value"]

    def add_cookie(self, cookie_key: str = "", cookie_val: str = ""):
        if cookie_key:
            self.driver.add_cookie({"name": cookie_key, "value": cookie_val})

    def delete_cookies(self, cookie_name: str = ""):
        if cookie_name:
            self.driver.delete_cookie(cookie_name)
        else:
            self.driver.delete_all_cookies()

    def load(self, url):
        self.driver.get(url)

    def refresh(self):
        self.driver.get(self.current_url)

    def dismiss_alert(self):
        try:
            self.driver.switch_to.alert.dismiss()
        except NoAlertPresentException:
            return

    def is_at_main(self) -> bool:
        url = URL(self.current_url)
        return url.path == "/main/Main.do"

    def page_source(self):
        return self.driver.page_source

    def quit(self):
        self.driver.quit()

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.driver.quit()
        except Exception:
            pass