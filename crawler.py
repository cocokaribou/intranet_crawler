from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from browser import Browser
from models import Employee, Input, LoginResult
from config.intranet_config import BASE_DOMAIN, SESSION_COOKIE_KEY


class Crawler:
    session_cookie = ""

    '''
    login
    '''
    def login(self, usr_input: Input) -> LoginResult:
        with Browser(BASE_DOMAIN) as browser:
            try:
                input_id = WebDriverWait(browser, 1).until(
                    EC.presence_of_element_located((By.ID, 'login_id'))
                )
                input_id.send_keys(usr_input.id)

                input_pw = WebDriverWait(browser, 1).until(
                    EC.presence_of_element_located((By.ID, 'password'))
                )
                input_pw.send_keys(usr_input.password)
                input_pw.send_keys(Keys.ENTER)

                if browser.is_at_main():
                    self.session_cookie = browser.get_cookie(SESSION_COOKIE_KEY)
                    return LoginResult(code=1000, msg="login success!")

                else:
                    self.session_cookie = ""
                    return LoginResult(code=9999, msg="login fail!")

            except UnexpectedAlertPresentException as e:
                self.session_cookie = ""
                return LoginResult(code=9999, msg=e.alert_text)

    '''
    get user info list
    '''
    def scrap_employee_list(self) -> list[Employee]:
        with Browser(BASE_DOMAIN) as browser:
            browser.add_cookie(SESSION_COOKIE_KEY, self.session_cookie)

            try:
                browser.execute_script(
                    f"window.location.href='{BASE_DOMAIN}"
                    + "/employee/employeeMgmt.do?method=selectEmployeeList&rowsPerPage=300&enter_yn=Y'")

                return list(
                    map(lambda x: Employee.init_from_list(image=x.find_element(By.TAG_NAME, 'img').get_attribute('src'),
                                                          input_string=x.text),
                        browser.find_multiple(By.TAG_NAME, 'table')[5].find_elements(By.TAG_NAME, 'tr')[1:]))

            except Exception:
                return list()

    '''
    get my info
    '''
    def scrap_my_information(self) -> Employee:
        with Browser(BASE_DOMAIN) as browser:
            browser.add_cookie(SESSION_COOKIE_KEY, self.session_cookie)

            try:
                browser.execute_script(
                    f"window.location.href='{BASE_DOMAIN}"
                    + "/employee/employeeMgmt.do?method=modifyNewEmployee'")

                table = browser.find_multiple(By.TAG_NAME, 'table')[1]
                return Employee(
                    id=(lambda x: x.get_attribute("value"))(table.find_elements(By.TAG_NAME, 'input')[0]),
                    idx=(lambda x: x.get_attribute("value"))(table.find_elements(By.TAG_NAME, 'input')[3]),
                    name=(lambda x: x.get_attribute("value"))(table.find_elements(By.TAG_NAME, 'input')[4]),
                    department=(lambda x: x.get_attribute("value"))(table.find_elements(By.TAG_NAME, 'input')[13]),
                    image=(lambda x: x.get_attribute("src"))(table.find_elements(By.TAG_NAME, 'img')[1]),
                    position=(lambda x: Select(x).first_selected_option.text)(table.find_element(By.TAG_NAME, "select"))
                )

            except Exception:
                return Employee()

    '''
    logout by deleting session cookie
    '''
    def logout(self) -> LoginResult:
        self.session_cookie = ""
        return LoginResult(code=1000, msg="logout success!")

