from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# chrome driver browser

class Browser:
    def __init__(self, base_domain):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        self.driver.get(base_domain)
        self.driver.implicitly_wait(5)

    @property
    def current_url(self):
        return self.driver.current_url

    def implicitly_wait(self, t):
        self.driver.implicitly_wait(t)

    # default : find_element_by_id
    def find_single(self, value, selector=By.ID):
        try:
            return self.driver.find_element(selector, value)
        except NoSuchElementException:
            return None

    def find_multiple(self, selector, id):
        try:
            return self.driver.find_elements(selector, id)
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

    def delete_cookies(self, cookie_name: str = ""):
        if cookie_name:
            self.driver.delete_cookie(cookie_name)
        else:
            self.driver.delete_all_cookies()

    def refresh(self):
        self.driver.get(self.current_url)

    def quit(self):
        self.driver.quit()

    def __del__(self):
        try:
            self.driver.quit()
        except Exception:
            pass
