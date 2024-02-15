from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from browser import Browser
from models import Employee
from config.intranet_config import BASE_DOMAIN, SESSION_COOKIE_KEY


def login(usr_id, usr_pwd) -> str:
    with Browser(BASE_DOMAIN) as browser:
        try:
            input_id = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located((By.ID, 'login_id'))
            )
            input_id.send_keys(usr_id)

            input_pw = WebDriverWait(browser, 1).until(
                EC.presence_of_element_located((By.ID, 'password'))
            )
            input_pw.send_keys(usr_pwd)
            input_pw.send_keys(Keys.ENTER)

            if browser.is_at_main():
                session_cookie = browser.get_cookie(SESSION_COOKIE_KEY)

            else:
                session_cookie = ""

        except UnexpectedAlertPresentException as e:
            session_cookie = ""

        finally:
            return session_cookie


def scrap_employee_list(token) -> list[Employee]:
    with Browser(BASE_DOMAIN) as browser:
        browser.add_cookie(SESSION_COOKIE_KEY, token)

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


def scrap_my_information(token) -> Employee:
    with Browser(BASE_DOMAIN) as browser:
        browser.add_cookie(SESSION_COOKIE_KEY, token)

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